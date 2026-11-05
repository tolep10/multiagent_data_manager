import { MyDir, MyFile } from "./models.js"
import { APIsService } from "./apisService.js";

export class DOMManager {
    constructor() {
        this.ulRoot = document.querySelector('#root-tree');
        this.service = new APIsService();
    }

    buildTree(myDir) {
        this.ulRoot.innerHTML = "";
        this.buildElements(myDir, this.ulRoot);
    }

    buildElements(myDir, ulCurrent) {
        if (myDir instanceof MyDir) {
            const isOpen = !myDir.isEmpty();
            const liElement = this.buildHTMLli(myDir, isOpen);
            
            ulCurrent.appendChild(liElement);

            if (!myDir.isEmpty()) {
                let ulElement = document.createElement("ul");

                myDir.dirs.forEach(element => {
                    this.buildElements(element, ulElement);
                })

                liElement.appendChild(ulElement);
            }
        } else if (myDir instanceof MyFile) {
            const liElement = this.buildHTMLli(myDir, false);
            ulCurrent.appendChild(liElement);
        }

    }

    buildHTMLli(myElement, isOpen) {
        if (myElement.name == "") {
            myElement.name = ".";
        }

        const myElementName = myElement.name.length > 8 ? myElement.name.slice(0, 7) + '...' : myElement.name;

        let liElement = document.createElement("li");
        liElement.setAttribute('title', myElement.name);

        let spanElement = document.createElement("SPAN");
        spanElement.innerText = " " + myElementName;

        if (myElement instanceof MyDir) {
            liElement.addEventListener("dblclick", (evt) => {
               this.processDblClickFolder(evt, myElement);
            });
            
            spanElement.classList.add(isOpen ? "folder-open" : "folder-close");
            spanElement.classList.add("folder-all");

        } else if (myElement instanceof MyFile) {
            liElement.addEventListener("dblclick", (evt) => {
                this.processDblClickFile(evt, myElement);
            })
            const classFile = this.defineCSSClassFile(myElement.ext);
            spanElement.classList.add(classFile);
            spanElement.classList.add("file-all");
        }

        liElement.appendChild(spanElement);

        return liElement;
    }

    processDblClickFolder(evt, myElement) {
        evt.stopPropagation();
        this.service.sendExplorerRequest(myElement.path);
    }

    processDblClickFile(evt, myElement) {
         evt.stopPropagation();
         this.service.sendOpenFileRequest(myElement.path);
    }

    defineCSSClassFile(fileExt) {
        if (fileExt.toLowerCase() == ".pdf") {
            return "file-pdf";
        }

        if (fileExt.toLowerCase() == ".docx") {
            return "file-word";
        }

        if (fileExt.toLowerCase() == ".xlsx" || fileExt.toLowerCase() == ".csv") {
            return "file-excel";
        }

        if ([".png", ".jpg", ".jpeg", ".gif", ".svg"].includes(fileExt.toLowerCase())) {
            return "file-image";
        }

        if ([".mp3", ".mp4", ".avi", ".mpeg"].includes(fileExt.toLowerCase())) {
            return "file-media";
        }

        if (fileExt.toLowerCase() == ".py") {
            return "file-py";
        }

        if (fileExt.toLowerCase() == ".txt") {
            return "file-txt";
        }

        return "file-icon";

    }
}