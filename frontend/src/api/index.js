import http from './http'

export const getOverview = () => http.get('/api/statistics/overview')
export const getBehaviorSummary = () => http.get('/api/statistics/behavior-summary')
export const getAttendanceTrend = () => http.get('/api/statistics/attendance-trend')
export const getTrendByClassCourse = (courseId, classId) => {
  const params = {}
  if (courseId) params.course_id = courseId
  if (classId) params.class_id = classId
  return http.get('/api/statistics/attendance-trend/filter', { params })
}

export const getCourses = () => http.get('/api/courses')
export const createCourse = data => http.post('/api/courses', data)
export const updateCourse = (id, data) => http.put(`/api/courses/${id}`, data)
export const deleteCourse = id => http.delete(`/api/courses/${id}`)

export const getClasses = () => http.get('/api/classes')
export const createClass = data => http.post('/api/classes', data)
export const updateClass = (id, data) => http.put(`/api/classes/${id}`, data)
export const deleteClass = id => http.delete(`/api/classes/${id}`)

export const uploadAnalyze = form => http.post('/api/upload/analyze', form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

export const getSessions = params => http.get('/api/sessions', { params })
export const getSession = id => http.get(`/api/sessions/${id}`)
export const getSessionAnalysis = id => http.get(`/api/sessions/${id}/analysis`)
export const deleteSession = id => http.delete(`/api/sessions/${id}`)
export const getBehaviorCategories = () => http.get('/api/behavior-categories')
