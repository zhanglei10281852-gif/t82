import request from '@/utils/request'

export function getHolidays(params) {
  return request.get('/holidays', { params })
}

export function createHoliday(data) {
  return request.post('/holidays', data)
}

export function deleteHoliday(id) {
  return request.delete(`/holidays/${id}`)
}
