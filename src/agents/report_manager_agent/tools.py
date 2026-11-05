from datetime import datetime
from typing import List, Any, Tuple, Annotated
from pathlib import Path

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from openpyxl.worksheet.worksheet import Worksheet
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from ...utils import settings


class ReportManagerAgent:
    def __init__(self):
        self._path_base = Path(settings.REPORTS_PATH).resolve()



    async def generate_excel_report(self, type_report: str, path_to_report: str, state: Annotated[dict,InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
        """
        Generates a professional Excel report from previously extracted agent data, returns the creation path including the report name.
        """
        try:
            data = state.get("extracted_data", [])
            if not data:
                raise RuntimeError("No data was found in the state to generate the report. Make sure to extract the information first.")

            target_path = Path(f"{self._path_base}/{path_to_report}").resolve()

            if not target_path.is_relative_to(self._path_base):
                raise RuntimeError("Access denied, outside the sandbox.")

            if not target_path.exists():
                raise RuntimeError(f"'{path_to_report}' doesn't exist.")

            report_name = self._generate_report_name(type_report)
            final_path = Path(f"{self._path_base}/{path_to_report}/{report_name}").resolve()

            workbook = Workbook()
            worksheet = workbook.create_sheet(title="Data Report")

            ReportManagerAgent._write_data_table(worksheet, data)

            workbook.save(final_path)
            workbook.close()

            print(f"SUCCESS: report successfully generated: {path_to_report}/{report_name}")
            return Command(
                update={
                    "progress": {"report_generated": f"SUCCESS: report successfully generated: {path_to_report}/{report_name}"},
                    "messages": [
                        ToolMessage(
                            content=f"SUCCESS: report successfully generated: {path_to_report}/{report_name}",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )


        except Exception as e:
            msg_error = f"ERROR: generating Excel file: {str(e)}"
            print(msg_error)
            return Command(
                update={
                    "progress": {"report_generated": f"ERROR: generating Excel file: {str(e)}"},
                    "messages": [
                        ToolMessage(
                            content=msg_error,
                            tool_call_id=tool_call_id,
                            #status="error"  # Esto le indica explícitamente a la plataforma/grafo que la ejecución falló
                        )
                    ]
                }
            )


    async def add_sheet_report(self, sheet_name: str, report_path: str, state: Annotated[dict,InjectedState], tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
        """
        Adds a new worksheet to an existing Excel report using data previously extracted by another agent.
        """
        try:
            data = state.get("extracted_data", [])
            if not data:
                raise RuntimeError("No data was found in the state to generate the report. Make sure to extract the information first.")


            final_path = Path(f"{self._path_base}/{report_path}").resolve()

            if not final_path.is_relative_to(self._path_base):
                raise RuntimeError("Access denied, outside the sandbox.")

            if not final_path.exists():
                raise RuntimeError(f"'{report_path}' doesn't exist.")

            workbook = load_workbook(final_path)
            counter = 2

            while sheet_name in workbook.sheetnames:
                sheet_name = f"{sheet_name}_{counter}"

            worksheet = workbook.create_sheet(title=sheet_name)

            ReportManagerAgent._write_data_table(worksheet, data)

            workbook.save(final_path)
            workbook.close()


            return Command(
                update={
                    "progress": {"sheet_aggregated": f"SUCCESS: Information stored in the sheet {sheet_name}"},
                    "messages": [
                        ToolMessage(
                            content=f"SUCCESS: Information stored in the sheet {sheet_name}",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        except Exception as e:
            msg_error = f"ERROR: an error occurred while generating the new sheet with the information {str(e)}"
            print(msg_error)
            return Command(
                update={
                    "progress": {"sheet_aggregated": f"ERROR: an error occurred while generating the new sheet with the information {str(e)}"},
                    "messages": [
                        ToolMessage(
                            content=f"ERROR: an error occurred while generating the new sheet with the information {str(e)}",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )


    def _generate_report_name(self, report_type: str) -> str:
        typed_sanitized = report_type.lower().replace(" ", "_")

        current_date = datetime.now().strftime("%Y%m%d")
        report_name = f"{current_date}_{typed_sanitized}.xlsx"

        final_path = self._path_base.joinpath(report_name)

        if final_path.exists():
            counter = 1
            base_name = final_path.stem
            extension = final_path.suffix

            while final_path.exists():
                counter += 1
                report_name = f"{base_name}_{counter}{extension}"
                final_path = self._path_base / report_name


        return report_name


    @staticmethod
    def _identify_and_convert_xl(value) -> Tuple[Any, ...]:
        """Determines and returns the data type of cell"""

        if isinstance(value, str):
            formats = [
                # Formats con hora (datetime)
                ("%Y-%m-%d %H:%M:%S", "datetime", True), ("%Y-%m-%d %H:%M", "datetime", True),
                ("%d/%m/%Y %H:%M:%S", "datetime", True), ("%d/%m/%Y %H:%M", "datetime", True),
                ("%m/%d/%Y %H:%M:%S", "datetime", True), ("%m/%d/%Y %H:%M", "datetime", True),
                ("%m/%d/%Y %I:%M %p", "datetime", True), ("%m/%d/%y %I:%M %p", "datetime", True),

                # Formats sin hora (date)
                ("%Y-%m-%d", "date", False), ("%Y/%m/%d", "date", False),
                ("%d/%m/%Y", "date", False), ("%d-%m-%Y", "date", False),
                ("%m/%d/%Y", "date", False), ("%m-%d-%Y", "date", False),
                ("%m/%d/%y", "date", False), ("%m-%d-%y", "date", False)
            ]

            for date_format, type_name, has_time in formats:
                try:
                    date_object = datetime.strptime(value, date_format)
                    # Return el tipo de dato y el object date real (no texto)
                    return type_name, date_object if has_time else date_object.date()
                except ValueError:
                    continue

        # Si no es texto de date, return su tipo nativo y su valor original
        return type(value).__name__, value


    @staticmethod
    def _write_data_table(worksheet: Worksheet, data: List[Any]) -> None:
        """
        Write a data table in an openpyxl sheet, apply styles to the headers, date formats, and adjust the column widths.
        """

        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        header_font = Font(bold=True)
        header_fill = PatternFill(start_color="D7E4BC", end_color="D7E4BC", fill_type="solid")

        # get headers from the keys del primer dic
        headers = list(data[0].keys())

        # write headers (Fila 1, Columnas 1 a N)
        for col_num, header in enumerate(headers, start=1):
            cell = worksheet.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = thin_border

        # Formats de date compatibles con Excel
        date_format = 'yyyy-mm-dd'
        datetime_format = 'yyyy-mm-dd hh:mm'

        # write rows de data (start in the row 2)
        for row_num, row_data in enumerate(data, start=2):
            for col_num, header in enumerate(headers, start=1):
                value = row_data.get(header, "")

                data_type, processed_value = ReportManagerAgent._identify_and_convert_xl(value)

                cell = worksheet.cell(row=row_num, column=col_num, value=processed_value)

                if data_type == "date":
                    cell.number_format = date_format
                elif data_type == "datetime":
                    cell.number_format = datetime_format
                # Nota: 'int', 'float' y 'bool' does not require format of text en openpyxl


        for col_num, header in enumerate(headers, start=1):
            col_letter = get_column_letter(col_num)
            worksheet.column_dimensions[col_letter].width = len(str(header)) + 5



report_manager_agent = ReportManagerAgent()

report_manager_agent_tools = [
    tool(report_manager_agent.generate_excel_report),
    tool(report_manager_agent.add_sheet_report),
]