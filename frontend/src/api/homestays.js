import request from '@/utils/request'

export function getHomestays(params) {
  return request.get('/homestays', { params })
}

export function getHomestay(id) {
  return request.get(`/homestays/${id}`)
}

export function createHomestay(data) {
  return request.post('/homestays', data)
}

export function updateHomestay(id, data) {
  return request.put(`/homestays/${id}`, data)
}

export function deleteHomestay(id) {
  return request.delete(`/homestays/${id}`)
}
