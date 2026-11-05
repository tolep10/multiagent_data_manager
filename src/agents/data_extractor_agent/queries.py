sql_queries_dict = {
    "simply_db_tables_info" : """
                        SELECT table_name 
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name;
                        """,
                        
    "full_db_tables_info": """
                            SELECT
                            tc.table_name AS nombre_tabla,
                            array_agg(kcu.column_name) AS columnas_primarias,
                            (
                                SELECT string_agg(
                                    CONCAT(
                                        kcu2.column_name,
                                        ' (referencia a ', ccu.table_name,
                                        '.' , ccu.column_name, ')'
                                    ),
                                    ', '
                                )
                                FROM information_schema.table_constraints tc2
                                JOIN information_schema.key_column_usage kcu2 ON tc2.constraint_name = kcu2.constraint_name
                                JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc2.constraint_name
                                WHERE tc2.constraint_type = 'FOREIGN KEY'
                                AND tc2.table_name = tc.table_name
                                AND tc2.table_schema = 'public'
                            ) AS claves_foraneas
                        FROM
                            information_schema.table_constraints tc
                        JOIN
                            information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                        WHERE
                            tc.constraint_type = 'PRIMARY KEY'
                            AND tc.table_schema = 'public'
                        GROUP BY
                            tc.table_name
                        ORDER BY
                            tc.table_name;
                        """,
    
    "simply_table_info" : """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        AND table_schema = 'public';
                        """,
    
                
    "full_table_info" : """
                        SELECT
                        c.table_name,
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        CASE
                            WHEN c.column_name IN (
                                SELECT kcu.column_name
                                FROM information_schema.table_constraints tc
                                JOIN information_schema.key_column_usage kcu
                                    ON tc.constraint_name = kcu.constraint_name
                                WHERE tc.constraint_type = 'PRIMARY KEY'
                                    AND tc.table_name = c.table_name
                            ) THEN 'Sí'
                            ELSE 'No'
                        END AS es_clave_primaria,
                        CASE
                            WHEN c.column_name IN (
                                SELECT kcu.column_name
                                FROM information_schema.table_constraints tc
                                JOIN information_schema.key_column_usage kcu
                                    ON tc.constraint_name = kcu.constraint_name
                                WHERE tc.constraint_type = 'FOREIGN KEY'
                                    AND tc.table_name = c.table_name
                            ) THEN 'Sí'
                            ELSE 'No'
                        END AS es_clave_foranea
                    FROM
                        information_schema.columns c
                    WHERE
                        c.table_name = %s
                        AND c.table_schema = 'public'
                    ORDER BY
                        c.ordinal_position;
                    """,
    
    
}