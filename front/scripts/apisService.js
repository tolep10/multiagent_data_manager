import { ExplorerRequest, UserRequest } from "./requests.js"

export class APIsService {
    constructor() {
        this.URL_BASE = "http://localhost:8001/api"; 
        this.endpointExplorer = "/explorer/tree";
        this.endpointAgent = "/agent"
        this.openFile = "/open-file"
    }

    async sendExplorerRequest(path) {
        try {
            const req = new ExplorerRequest(path);
            const response = await fetch(`${this.URL_BASE}${this.endpointExplorer}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(req) // Convertimos el objeto JS a un string JSON válido
            });

            // Verificamos si la respuesta HTTP es correcta (status 200-299)
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.content || `Error en el servidor: ${response.status}`);
            }

            // Si todo sale bien, procesamos la respuesta de la API
            const data = await response.json();
            console.log("Acción ejecutada con éxito:", data.content);

        } catch (error) {
            console.error(`Error al llamar al endpoint ${this.endpointExplorer}:`, error.message);
            alert("Error al actualizar el árbol de archivos")
        }
    }

    async sendAgentRequest(userPrompt) {
        try {
            const req = new UserRequest(userPrompt);
            const response = await fetch(`${this.URL_BASE}${this.endpointAgent}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(req) // Convertimos el objeto JS a un string JSON válido
            });

            // Verificamos si la respuesta HTTP es correcta (status 200-299)
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.content || `Error en el servidor: ${response.status}`);
            }

            // Si todo sale bien, procesamos la respuesta de la API
            const data = await response.json();
            console.log("Acción ejecutada con éxito:", data.content);

            return data

        } catch (error) {
            console.log(error.message);
            console.error(`Error al llamar al endpoint ${this.endpointAgent}:`, error.message);
            alert("Error al ejecutar el agente");
            return null;
        }
    }

    async sendOpenFileRequest(path) {
        try {
            const req = new ExplorerRequest(path);
            const response = await fetch(`${this.URL_BASE}${this.openFile}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(req) // Convertimos el objeto JS a un string JSON válido
            });

            // Verificamos si la respuesta HTTP es correcta (status 200-299)
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.content || `Error en el servidor: ${response.status}`);
            }

            // Si todo sale bien, procesamos la respuesta de la API
            const data = await response.json();
            console.log("Acción ejecutada con éxito:", data.content);

            return data

        } catch (error) {
            console.log(error.message);
            console.error(`Error al llamar al endpoint ${this.openFile}:`, error.message);
            alert("Error al abrir el archivo");
        }
    }
}