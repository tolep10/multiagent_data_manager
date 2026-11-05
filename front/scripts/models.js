class Element {
    constructor(data) {
        Object.assign(this, data);
    }
}

export class MyFile extends Element {
    constructor(data) {
        super(data);
    }
    
    // saber si un archivo es imágen
    isImage() {
        const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg'];
        return imageExtensions.includes(this.ext?.toLowerCase());
    }
}

export class MyDir extends Element {
    constructor(data) {
        super(data);
        
        // Si tiene elementos en el array, los mapeamos según su tipo
        if (this.dirs && Array.isArray(this.dirs)) {
            this.dirs = this.dirs.map(item => {
                if (item.type === 'dir') {
                    return new MyDir(item); // Instancia recursiva
                } else if (item.type === 'file') {
                    return new MyFile(item); // Instancia de archivo
                }
                return item; // Por si acaso viene un tipo desconocido
            });
        }
    }

    
    isEmpty() {
        return (!this.dirs || this.dirs.length === 0);
    }
}
