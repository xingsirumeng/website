import axios from 'axios'

const api = axios.create({
  baseURL: 'http://139.196.32.236:8000',
  timeout: 10000,
})

export default api
