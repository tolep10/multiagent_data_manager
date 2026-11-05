import { DOMManager } from "./DOMManager.js"; 
import { MyDir } from "./models.js"

export class WSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 3000; // 3 segundos
        this.reconnectTimeoutId = null;
        this.dom = new DOMManager()
    }  

    connectToWebSocket() {
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
        }

         if (this.ws) {
            this.ws.close();
        }

        // Usa ws:// para desarrollo o wss:// si tu API usa HTTPS en producción
        this.ws = new WebSocket("ws://localhost:8001/api/ws/live-data");

        this.ws.onopen = (event) => {
            console.log("Conectado al servidor WebSocket.");
        };

        this.ws.onmessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                this.processMessage(response);
            } catch (error) {
                console.error("El mensaje no es un JSON válido:", error);
            }
        };

        this.ws.onclose = (event) => {
            console.warn("Conexión cerrada. Intentando reconectar...");
            // Guardamos el ID del timeout para poder cancelarlo si es necesario
            this.reconnectTimeoutId = setTimeout(() => this.connectToWebSocket(), this.reconnectInterval);
        };

        this.ws.onerror = (error) => {
            console.error("Error detectado en el WebSocket:", error);
            this.ws.close();
        };
    }

    processMessage(response) {
        if (!response.error) {
            if (response.content !== undefined) {
                const myDir = new MyDir(response.content)
                this.dom.buildTree(myDir)
            } else {
                console.log("El content es nulo")
            }
        } else {
            console.log("Error al recibir la data" + JSON.stringify(response));
        }
    }


    disconnect() {
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
        }
        if (this.ws) {
            // Removemos el listener para que no intente reconectar al cerrar a propósito
            this.ws.onclose = null; 
            this.ws.close();
            console.log("WebSocket desconectado manualmente.");
        }
    }
}