import axios from 'axios'

const api = axios.create({
  baseURL: 'https://139.196.32.236.nip.io',
  timeout: 10000,
})

export default api
