import request from '@/utils/request'

export function getMaintenances(params) {
  return request.get('/maintenance', { params })
}

export function createMaintenance(data) {
  return request.post('/maintenance', data)
}

export function deleteMaintenance(id) {
  return request.delete(`/maintenance/${id}`)
}
