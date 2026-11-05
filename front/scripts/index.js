import { WSocketManager } from "./wSocket.js"
import { AgentRequestManager } from "./agentRequest.js"

export class MainClass {
    constructor() {
        this.ws = new WSocketManager()
        this.agentRequestManager = new AgentRequestManager()
    }

    launchSocket() {
        this.ws.connectToWebSocket()
    }

}

document.addEventListener("DOMContentLoaded", () => {
    const mainclass = new MainClass()
    mainclass.launchSocket()
})