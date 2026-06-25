function getToken(): string | null {
    return localStorage.getItem('token')
}

function setToken(token: string): void{
    localStorage.setItem('token',token)
}

function clearToken(): void{
    localStorage.removeItem('token')
}

function isAuthenticated(): boolean{
    if (localStorage.getItem('token')){
        return true
    }
    return false
}