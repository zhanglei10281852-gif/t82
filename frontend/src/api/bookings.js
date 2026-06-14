import request from '@/utils/request'

export function getBookings(params) {
  return request.get('/bookings', { params })
}

export function getBooking(id) {
  return request.get(`/bookings/${id}`)
}

export function createBooking(data) {
  return request.post('/bookings', data)
}

export function updateBookingStatus(id, data) {
  return request.put(`/bookings/${id}/status`, data)
}

export function calculatePrice(data) {
  return request.post('/bookings/calculate-price', data)
}
