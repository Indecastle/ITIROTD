export function find_cookie(key) {
    return ar.find((item) => item.trim().startsWith(key + '=')).split('=', 2)[1]
}