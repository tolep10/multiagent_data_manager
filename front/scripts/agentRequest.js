import { APIsService } from "./apisService.js"

export class AgentRequestManager {
    constructor() {
        this.btnRequest = document.getElementById("btn-request")
        this.btnRequest.addEventListener("click", (evt) => {
            this.sendRequest(evt)
        })
        this.inputUser = document.getElementById("input-user")
        this.chatSection = document.getElementById("chat-section")
        this.apiService = new APIsService()
    }

    async sendRequest(evt) {
        evt.target.disabled = true
        let userPrompt = this.inputUser.value

        if (!userPrompt.trim()) {
            alert("Ingresa una consulta para el agente")
            return
        }


        const divUser = this.buildSectionUserRequest(userPrompt)
        this.chatSection.appendChild(divUser)
        this.inputUser.value = ""
        const divSpinner = this.buildThinking()
        this.chatSection.appendChild(divSpinner)


        let result = await this.apiService.sendAgentRequest(userPrompt)

        let messageResponse = ""

        if (result) {
            if (!result.error) {
                messageResponse += result.content
            } else {
                 messageResponse += "Error al obtener respuesta del agente..."
                 console.log(result.content)
            }

        } else {
            messageResponse += "Error al conectar con el agente..."
        }

        this.chatSection.removeChild(divSpinner)
        
        const divAgent = this.buildSectionAgentResponse(messageResponse)
        this.chatSection.appendChild(divAgent)

        evt.target.disabled = false
    }


    buildSectionUserRequest(userPrompt) {
        let divMain = document.createElement("div")
        divMain.classList.add("message")
        divMain.classList.add("user-message")
        let divChild = document.createElement("div")
        divChild.classList.add("message-content")
        divChild.innerText = userPrompt
        divMain.appendChild(divChild)

        return divMain
    }


    buildSectionAgentResponse(agentResponse) {
        let divMain = document.createElement("div")
        divMain.classList.add("message")
        divMain.classList.add("bot-message")
        let divChild = document.createElement("div")
        divChild.classList.add("message-content")
        divChild.innerText = agentResponse
        divMain.appendChild(divChild)

        return divMain
    }
    

    buildThinking() {
        let divMain = document.createElement("div")
        divMain.classList.add("message")
        divMain.classList.add("bot-message")
        let spinnerLoader = document.createElement("img")
        spinnerLoader.setAttribute("src", "img/spinner-icon-0.gif")
        spinnerLoader.style.width = "30px"
        spinnerLoader.style.height = "30px"
        divMain.appendChild(spinnerLoader)

        return divMain
    }
}