export class ExplorerRequest {
    constructor(path) {
        this.relative_path = path //el campo se debe llamar exactamente igual que a como se definio en el back, si no lanza error
    }
}
 
export class UserRequest {
    constructor(userRequest) {
        this.user_request = userRequest
    }
}
    