<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const API_BASE = (import.meta.env.VITE_API_URL || 'https://maktab-davomat-production.up.railway.app/api').replace(/\/$/, '')

const token = ref(localStorage.getItem('access') || '')
const refresh = ref(localStorage.getItem('refresh') || '')
const me = ref(JSON.parse(localStorage.getItem('me') || 'null'))
const activeTab = ref('dashboard')
const loading = ref(false)
const message = ref('')
const error = ref('')

const teachers = ref([])
const classrooms = ref([])
const students = ref([])
const malumotlar = ref({ students: [], classrooms: [], total_students: 0, total_classrooms: 0 })
const settings = ref(null)
const todayAttendance = ref(null)
const dashboard = ref(null)
const attendanceReport = ref({ classrooms: [], school_summary: {}, absent_students: [], days: [] })
const todayAbsentReport = ref({ classrooms: [], school_summary: {}, absent_students: [], days: [], selected_date: '' })
const teacherAttendanceReport = ref({ rows: [], summary: {}, teachers: [], days: [] })

const loginForm = reactive({ username: 'director', password: 'director123' })
const teacherForm = reactive({ full_name: '', login: '', parol: '', phone: '', subject: '' })
const classroomForm = reactive({ teacher: '', name: '', room: '', lesson_time: '', shift: 'morning' })
const studentForm = reactive({
  classroom: '',
  full_name_input: '',
  gender: 'male',
  phone_primary: '',
  father_full_name: '',
  father_phone: '',
  mother_full_name: '',
  mother_phone: '',
  address: '',
  birth_date: '',
})
const settingsForm = reactive({
  school_name: '',
  latitude: '',
  longitude: '',
  allowed_radius_meters: 120,
  work_start_time: '08:00',
  work_end_time: '17:00',
  late_after_minutes: 10,
})
const attendanceForm = reactive({ classroom_id: '', date: new Date().toISOString().slice(0, 10), records: {} })
const attendanceFilter = reactive({ date: new Date().toISOString().slice(0, 10), classroom: '' })
const teacherAttendanceFilter = reactive({ start_date: new Date().toISOString().slice(0, 10), end_date: new Date().toISOString().slice(0, 10), teacher: '' })
const searchText = ref('')
const filterClassroom = ref('')
const malumotlarSearch = ref('')
const malumotlarClassroom = ref('')
const malumotlarGender = ref('')
const todayAbsentClassroom = ref('')

const isLogged = computed(() => Boolean(token.value && me.value))
const role = computed(() => me.value?.role || '')
const isAdminLike = computed(() => role.value === 'director' || role.value === 'admin')
const isDirector = computed(() => role.value === 'director')
const isAdmin = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher')
const canCreateStudent = computed(() => role.value === 'admin' || role.value === 'teacher')
const canEnterAttendance = computed(() => role.value === 'admin' || role.value === 'teacher')
const currentName = computed(() => me.value?.full_name || me.value?.username || '')

const stats = computed(() => [
  { label: 'Ustozlar', value: teachers.value.length, hint: 'Admin yaratgan ustozlar' },
  { label: 'Sinflar', value: classrooms.value.length, hint: 'Faol sinflar' },
  { label: "O'quvchilar", value: students.value.length, hint: isDirector.value ? 'Director faqat ko‘radi' : 'Sinfga biriktirilganlar' },
  { label: 'Ma’lumotlar', value: malumotlar.value.total_students || students.value.length, hint: 'Excelga yuklanadi' },
])

const visibleTabs = computed(() => {
  const base = [{ id: 'dashboard', label: 'Dashboard' }]
  if (isTeacher.value) base.push({ id: 'checkin', label: 'Ishga keldim' })
  if (isAdmin.value) base.push({ id: 'teachers', label: 'Ustozlar' })
  base.push({ id: 'classrooms', label: 'Sinflar' })
  base.push({ id: 'students', label: "O'quvchilar" })
  base.push({ id: 'malumotlar', label: 'Ma’lumotlar' })
  base.push({ id: 'today-absent', label: 'Bugun kelmaganlar' })
  base.push({ id: 'attendance', label: 'Davomat' })
  if (isAdminLike.value) base.push({ id: 'teacher-attendance', label: 'Ustoz davomati' })
  return base
})

const filteredStudents = computed(() => {
  const s = searchText.value.trim().toLowerCase()
  return students.value.filter((item) => {
    const matchesClass = !filterClassroom.value || String(item.classroom) === String(filterClassroom.value)
    const text = [item.full_name, item.birth_date, item.phone_primary, item.father_full_name, item.father_phone, item.mother_full_name, item.mother_phone, item.address, item.classroom_name]
      .join(' ')
      .toLowerCase()
    return matchesClass && (!s || text.includes(s))
  })
})

const filteredMalumotlarStudents = computed(() => {
  const s = malumotlarSearch.value.trim().toLowerCase()
  const rows = Array.isArray(malumotlar.value?.students) ? malumotlar.value.students : []
  return rows.filter((item) => {
    const matchesClass = !malumotlarClassroom.value || String(item.classroom) === String(malumotlarClassroom.value)
    const matchesGender = !malumotlarGender.value || item.gender === malumotlarGender.value
    const text = [
      item.full_name, item.birth_date, item.gender_display, item.phone_primary,
      item.father_full_name, item.father_phone, item.mother_full_name, item.mother_phone,
      item.address, item.classroom_name, item.teacher_name,
    ].join(' ').toLowerCase()
    return matchesClass && matchesGender && (!s || text.includes(s))
  })
})

const selectedMalumotlarClassroom = computed(() => {
  if (!malumotlarClassroom.value) return null
  const list = Array.isArray(malumotlar.value?.classrooms) ? malumotlar.value.classrooms : classrooms.value
  return list.find((item) => String(item.id) === String(malumotlarClassroom.value)) || null
})

const selectedMalumotlarClassroomTotal = computed(() => {
  const rows = Array.isArray(malumotlar.value?.students) ? malumotlar.value.students : []
  if (!malumotlarClassroom.value) return rows.length
  return rows.filter((item) => String(item.classroom) === String(malumotlarClassroom.value)).length
})

const todayAbsentClassrooms = computed(() => {
  const rows = Array.isArray(todayAbsentReport.value?.classrooms) ? todayAbsentReport.value.classrooms : []
  if (!todayAbsentClassroom.value) return rows
  return rows.filter((item) => String(item.id) === String(todayAbsentClassroom.value))
})

const todayAbsentStudents = computed(() => {
  const rows = Array.isArray(todayAbsentReport.value?.absent_students) ? todayAbsentReport.value.absent_students : []
  if (!todayAbsentClassroom.value) return rows
  return rows.filter((item) => String(item.classroom_id) === String(todayAbsentClassroom.value))
})

const todayAbsentFilteredSummary = computed(() => {
  const classrooms = todayAbsentClassrooms.value
  return classrooms.reduce((acc, classroom) => {
    acc.total_classrooms += 1
    acc.total_students += Number(classroom.student_count || 0)
    acc.present_count += Number(classroom.present_count || 0)
    acc.late_count += Number(classroom.late_count || 0)
    acc.unexcused_absent_count += Number(classroom.unexcused_absent_count || 0)
    acc.excused_count += Number(classroom.excused_count || 0)
    acc.total_absent_count += Number(classroom.total_absent_count || 0)
    acc.not_marked_count += Number(classroom.not_marked_count || 0)
    return acc
  }, {
    total_classrooms: 0,
    total_students: 0,
    present_count: 0,
    late_count: 0,
    unexcused_absent_count: 0,
    excused_count: 0,
    total_absent_count: 0,
    not_marked_count: 0,
  })
})

const selectedAttendanceClass = computed(() => classrooms.value.find((item) => String(item.id) === String(attendanceForm.classroom_id)))
const selectedAttendanceStudents = computed(() => students.value.filter((item) => String(item.classroom) === String(attendanceForm.classroom_id)))

function fillAttendanceFormFromReport() {
  const classroom = attendanceReport.value?.classrooms?.find((item) => String(item.id) === String(attendanceForm.classroom_id))
  if (!classroom?.students) return
  const nextRecords = {}
  classroom.students.forEach((student) => {
    if (student.status_key && student.status_key !== 'not_marked') {
      nextRecords[student.id] = {
        student_id: student.id,
        status: student.status_key,
        note: student.note || '',
      }
    }
  })
  attendanceForm.records = nextRecords
}

function showOk(text) {
  message.value = text
  error.value = ''
  setTimeout(() => { if (message.value === text) message.value = '' }, 3500)
}

function showErr(text) {
  error.value = text
  message.value = ''
}

function parseError(data) {
  if (!data) return 'Xatolik yuz berdi'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  const parts = []
  Object.entries(data).forEach(([key, value]) => {
    parts.push(`${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
  })
  return parts.join(' | ') || 'Xatolik yuz berdi'
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  if (token.value) headers.Authorization = `Bearer ${token.value}`
  let body = options.body
  if (body && !(body instanceof FormData) && !(body instanceof Blob)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers, body })
  if (response.status === 401 && refresh.value) {
    try {
      const refreshRes = await fetch(`${API_BASE}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refresh.value }),
      })
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json()
        token.value = refreshData.access
        localStorage.setItem('access', token.value)
        headers.Authorization = `Bearer ${token.value}`
        const retry = await fetch(`${API_BASE}${path}`, { ...options, headers, body })
        if (!retry.ok) throw await safeError(retry)
        return readResponse(retry, options.responseType)
      }
    } catch (err) {
      logout()
      throw err
    }
  }
  if (!response.ok) throw await safeError(response)
  return readResponse(response, options.responseType)
}

async function safeError(response) {
  try {
    const data = await response.json()
    return new Error(parseError(data))
  } catch (_) {
    return new Error(await response.text())
  }
}

async function readResponse(response, responseType) {
  if (responseType === 'blob') return response.blob()
  if (response.status === 204) return null
  const text = await response.text()
  return text ? JSON.parse(text) : null
}

async function login() {
  loading.value = true
  try {
    const auth = await api('/auth/token/', { method: 'POST', body: loginForm })
    token.value = auth.access
    refresh.value = auth.refresh
    localStorage.setItem('access', token.value)
    localStorage.setItem('refresh', refresh.value)
    me.value = await api('/auth/me/')
    localStorage.setItem('me', JSON.stringify(me.value))
    activeTab.value = 'dashboard'
    await loadAll()
    showOk('Tizimga muvaffaqiyatli kirdingiz')
  } catch (err) {
    showErr(err.message)
  } finally {
    loading.value = false
  }
}

function logout() {
  token.value = ''
  refresh.value = ''
  me.value = null
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('me')
}

async function loadAll() {
  if (!token.value) return
  loading.value = true
  try {
    await Promise.allSettled([loadTeachers(), loadClassrooms(), loadStudents(), loadMalumotlar(), loadSettings(), loadTodayAttendance(), loadDashboard(), loadAttendanceReport(), loadTodayAbsentReport(), loadTeacherAttendanceReport()])
  } finally {
    loading.value = false
  }
}

async function loadTeachers() {
  if (!isAdminLike.value) {
    teachers.value = []
    return
  }
  teachers.value = await api('/auth/teachers/')
}

async function loadClassrooms() {
  classrooms.value = await api('/classrooms/')
  if (!classroomForm.teacher && teachers.value[0]) classroomForm.teacher = teachers.value[0].id
  if (!studentForm.classroom && classrooms.value[0]) studentForm.classroom = classrooms.value[0].id
}

async function loadStudents() {
  students.value = await api('/students/')
}

async function loadMalumotlar() {
  const path = isAdminLike.value ? '/director/malumotlar/' : '/malumotlar/'
  malumotlar.value = await api(path)
}

async function loadSettings() {
  settings.value = await api('/school-settings/')
  if (settings.value) Object.assign(settingsForm, settings.value)
}

async function loadTodayAttendance() {
  if (!isTeacher.value) return
  try { todayAttendance.value = await api('/teacher-attendance/today/') } catch (_) {}
}

async function loadDashboard() {
  try { dashboard.value = await api('/dashboard/overview/') } catch (_) {}
}

async function loadAttendanceReport() {
  try {
    const params = new URLSearchParams()
    if (attendanceFilter.date) params.set('date', attendanceFilter.date)
    if (attendanceFilter.classroom) params.set('classroom', attendanceFilter.classroom)
    attendanceReport.value = await api(`/attendance/day-filter/?${params.toString()}`)
    if (canEnterAttendance.value && attendanceForm.classroom_id && String(attendanceFilter.classroom) === String(attendanceForm.classroom_id)) {
      fillAttendanceFormFromReport()
    }
  } catch (_) {}
}

async function loadTodayAbsentReport() {
  try {
    const today = new Date().toISOString().slice(0, 10)
    todayAbsentReport.value = await api(`/attendance/day-filter/?date=${today}`)
  } catch (_) {}
}

async function loadTeacherAttendanceReport() {
  if (!isAdminLike.value) return
  try {
    const params = new URLSearchParams()
    if (teacherAttendanceFilter.start_date) params.set('start_date', teacherAttendanceFilter.start_date)
    if (teacherAttendanceFilter.end_date) params.set('end_date', teacherAttendanceFilter.end_date)
    if (teacherAttendanceFilter.teacher) params.set('teacher', teacherAttendanceFilter.teacher)
    teacherAttendanceReport.value = await api(`/teacher-attendance/report/?${params.toString()}`)
  } catch (_) {}
}

async function createTeacher() {
  try {
    await api('/auth/teachers/', { method: 'POST', body: { ...teacherForm } })
    Object.assign(teacherForm, { full_name: '', login: '', parol: '', phone: '', subject: '' })
    await loadTeachers()
    showOk('Ustoz yaratildi')
  } catch (err) {
    showErr(err.message)
  }
}

async function deleteTeacher(id) {
  if (!confirm('Ustozni o‘chirasizmi?')) return
  try {
    await api(`/auth/teachers/${id}/`, { method: 'DELETE' })
    await loadTeachers()
    await loadClassrooms()
    showOk('Ustoz o‘chirildi')
  } catch (err) {
    showErr(err.message)
  }
}

async function createClassroom() {
  try {
    const name = (classroomForm.name || '').trim()
    if (!name) {
      showErr('Sinf nomini kiriting. Masalan: 9-A yoki 10-B')
      return
    }
    const payload = { ...classroomForm, name, subject: '' }
    if (!isAdminLike.value) delete payload.teacher
    await api('/classrooms/', { method: 'POST', body: payload })
    Object.assign(classroomForm, { teacher: teachers.value[0]?.id || '', name: '', room: '', lesson_time: '', shift: 'morning' })
    await loadClassrooms()
    await loadMalumotlar()
    showOk('Sinf yaratildi')
  } catch (err) {
    showErr(err.message)
  }
}


async function createStudent() {
  if (!canCreateStudent.value) {
    showErr('Director o‘quvchi yaratmaydi. Director faqat ma’lumotlarni ko‘radi va Excel yuklaydi.')
    return
  }
  try {
    const parts = (studentForm.full_name_input || '').trim().split(/\s+/).filter(Boolean)
    const payload = {
      ...studentForm,
      first_name: parts[0] || '',
      last_name: parts.slice(1).join(' '),
    }
    if (!payload.birth_date) delete payload.birth_date
    await api('/students/', { method: 'POST', body: payload })
    Object.assign(studentForm, {
      classroom: studentForm.classroom,
      full_name_input: '',
      gender: 'male',
      phone_primary: '',
      father_full_name: '',
      father_phone: '',
      mother_full_name: '',
      mother_phone: '',
      address: '',
      birth_date: '',
    })
    await loadStudents()
    await loadClassrooms()
    await loadMalumotlar()
    showOk('O‘quvchi saqlandi va sinfga biriktirildi')
  } catch (err) {
    showErr(err.message)
  }
}

async function saveSettings() {
  try {
    settings.value = await api('/school-settings/', { method: 'PUT', body: { ...settingsForm } })
    showOk('Sozlamalar saqlandi')
  } catch (err) {
    showErr(err.message)
  }
}

function getCurrentLocationPayload() {
  if (!navigator.geolocation) {
    throw new Error('Bu qurilmada lokatsiya aniqlanmadi. Iltimos, GPS/lokatsiyani yoqing.')
  }

  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: String(position.coords.latitude),
          longitude: String(position.coords.longitude),
        })
      },
      (geoError) => {
        const messages = {
          1: 'Lokatsiyaga ruxsat berilmadi. Iltimos, browserdan Location ruxsatini yoqing.',
          2: 'Lokatsiya aniqlanmadi. GPS yoki internetni tekshiring.',
          3: 'Lokatsiyani aniqlash vaqti tugadi. Qayta urinib ko‘ring.',
        }
        reject(new Error(messages[geoError.code] || 'Lokatsiya olishda xatolik yuz berdi.'))
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
    )
  })
}

async function teacherCheck(type) {
  try {
    const path = type === 'in' ? '/teacher-attendance/check-in/' : '/teacher-attendance/check-out/'
    const location = await getCurrentLocationPayload()
    todayAttendance.value = await api(path, { method: 'POST', body: location })
    showOk(todayAttendance.value.detail || 'Saqlandi')
  } catch (err) {
    showErr(err.message)
  }
}

function setAttendanceStatus(studentId, status) {
  attendanceForm.records[studentId] = { student_id: studentId, status, note: attendanceForm.records[studentId]?.note || '' }
}

function setAttendanceNote(studentId, note) {
  const current = attendanceForm.records[studentId] || { student_id: studentId, status: 'present', note: '' }
  current.note = note
  attendanceForm.records[studentId] = current
}

async function saveAttendance() {
  try {
    const records = selectedAttendanceStudents.value.map((student) => attendanceForm.records[student.id] || { student_id: student.id, status: 'present', note: '' })
    await api('/attendance/bulk-save/', { method: 'POST', body: { classroom_id: attendanceForm.classroom_id, date: attendanceForm.date, records } })
    attendanceFilter.date = attendanceForm.date
    attendanceFilter.classroom = attendanceForm.classroom_id
    await loadAttendanceReport()
    await loadTodayAbsentReport()
    await loadDashboard()
    showOk('Davomat saqlandi')
  } catch (err) {
    showErr(err.message)
  }
}

async function saveBlobAsExcel(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

async function downloadExcel() {
  try {
    const path = isAdminLike.value ? '/director/malumotlar/export/' : '/malumotlar/export/'
    const blob = await api(path, { responseType: 'blob' })
    await saveBlobAsExcel(blob, 'malumotlar-oquvchilar.xlsx')
  } catch (err) {
    showErr(err.message)
  }
}

async function downloadStudentsExcel() {
  try {
    const path = isAdminLike.value ? '/director/malumotlar/export/' : '/malumotlar/export/'
    const blob = await api(path, { responseType: 'blob' })
    await saveBlobAsExcel(blob, 'barcha-oquvchilar-malumotlari.xlsx')
  } catch (err) {
    showErr(err.message)
  }
}

async function downloadAttendanceExcel() {
  try {
    const params = new URLSearchParams()
    if (attendanceFilter.date) params.set('date', attendanceFilter.date)
    if (attendanceFilter.classroom) params.set('classroom', attendanceFilter.classroom)
    const blob = await api(`/attendance/day-filter/export/?${params.toString()}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'kunlik-davomat.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showErr(err.message)
  }
}

async function downloadTodayAbsentExcel() {
  try {
    const params = new URLSearchParams()
    params.set('date', todayAbsentReport.value?.selected_date || new Date().toISOString().slice(0, 10))
    params.set('absent_only', '1')
    if (todayAbsentClassroom.value) params.set('classroom', todayAbsentClassroom.value)
    const blob = await api(`/attendance/day-filter/export/?${params.toString()}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'bugun-kelmagan-oquvchilar.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showErr(err.message)
  }
}

async function downloadTeacherAttendanceExcel() {
  try {
    const params = new URLSearchParams()
    if (teacherAttendanceFilter.start_date) params.set('start_date', teacherAttendanceFilter.start_date)
    if (teacherAttendanceFilter.end_date) params.set('end_date', teacherAttendanceFilter.end_date)
    if (teacherAttendanceFilter.teacher) params.set('teacher', teacherAttendanceFilter.teacher)
    const blob = await api(`/teacher-attendance/report/export/?${params.toString()}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'ustozlar-davomati.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showErr(err.message)
  }
}

function shiftText(value) {
  return value === 'afternoon' ? 'Abetdan keyin' : 'Ertalab'
}

function dayName(dateText) {
  const days = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba']
  return days[new Date(dateText).getDay()] || ''
}

function formatDate(dateText) {
  if (!dateText) return '-'
  const date = new Date(dateText)
  if (Number.isNaN(date.getTime())) return dateText
  return date.toLocaleDateString('uz-UZ')
}

onMounted(async () => {
  if (isLogged.value) await loadAll()
})
</script>

<template>
  <main class="app-shell">
    <section v-if="!isLogged" class="login-page">
      <div class="login-card">
        <div class="brand-badge">Maktab CRM</div>
        <h1>Direktor, admin va ustoz paneli</h1>
        <p>Backend Railwayga, frontend Netlifyga tayyor. Login qilib tizimni boshqaring.</p>

        <form class="form-grid" @submit.prevent="login">
          <label>
            Login
            <input v-model="loginForm.username" placeholder="director" autocomplete="username" />
          </label>
          <label>
            Parol
            <input v-model="loginForm.password" type="password" placeholder="director123" autocomplete="current-password" />
          </label>
          <button class="primary-btn" :disabled="loading">Kirish</button>
        </form>


        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </section>

    <section v-else class="dashboard-layout">
      <aside class="sidebar">
        <div class="logo-block">
          <div class="logo-circle">CRM</div>
          <div>
            <b>Maktab CRM</b>
            <span>{{ currentName }} · {{ role }}</span>
          </div>
        </div>
        <nav>
          <button
            v-for="tab in visibleTabs"
            :key="tab.id"
            :class="['nav-item', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </nav>
        <button class="logout-btn" @click="logout">Chiqish</button>
      </aside>

      <section class="content">
        <header class="topbar">
          <div>
            <h2>{{ visibleTabs.find((t) => t.id === activeTab)?.label }}</h2>
            <p>Hafta kunlari Uzbekcha: Dushanba, Seshanba, Chorshanba, Payshanba, Juma, Shanba.</p>
          </div>
          <button class="ghost-btn" @click="loadAll">Yangilash</button>
        </header>

        <div v-if="message" class="success-msg">{{ message }}</div>
        <div v-if="error" class="error-msg">{{ error }}</div>

        <section v-if="activeTab === 'dashboard'" class="page-section">
          <div class="stats-grid">
            <article v-for="item in stats" :key="item.label" class="stat-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.hint }}</small>
            </article>
          </div>

          <div class="two-grid">
            <article class="panel-card">
              <h3>Bugungi sana</h3>
              <p class="big-date">{{ new Date().toLocaleDateString('uz-UZ') }}</p>
              <p>{{ dayName(new Date().toISOString()) }}</p>
            </article>
            <article class="panel-card">
              <h3>Tizim holati</h3>
              <p>Lokatsiya va ish vaqti sozlamalari yashirildi. Teacher faqat ishga kelish/ketishni bosadi.</p>
            </article>
          </div>
        </section>

        <section v-if="activeTab === 'checkin'" class="page-section">
          <div class="panel-card hero-card">
            <div>
              <h3>Teacher “Ishga keldim”</h3>
              <p>Ishga kelgan va ishdan ketgan vaqtlaringiz saqlanadi. Director bu ma’lumotlarni nazorat qiladi.</p>
            </div>
            <div class="action-row">
              <button class="primary-btn" @click="teacherCheck('in')">Ishga keldim</button>
              <button class="secondary-btn" @click="teacherCheck('out')">Ishdan ketdim</button>
            </div>
          </div>
          <article v-if="todayAttendance" class="panel-card">
            <h3>Bugungi holat</h3>
            <div class="info-grid">
              <span><b>Sana:</b> {{ todayAttendance.date }}</span>
              <span><b>Keldi:</b> {{ todayAttendance.check_in_time ? new Date(todayAttendance.check_in_time).toLocaleTimeString('uz-UZ') : '-' }}</span>
              <span><b>Ketdi:</b> {{ todayAttendance.check_out_time ? new Date(todayAttendance.check_out_time).toLocaleTimeString('uz-UZ') : '-' }}</span>
              <span><b>Ishlagan:</b> {{ todayAttendance.worked_hours || '-' }}</span>
            </div>
          </article>
        </section>

        <section v-if="activeTab === 'teachers' && isAdmin" class="page-section">
          <article class="panel-card">
            <h3>Ustoz yaratish</h3>
            <form class="wide-form" @submit.prevent="createTeacher">
              <label>Ism familyasi<input v-model="teacherForm.full_name" required placeholder="Ali Valiyev" /></label>
              <label>Login<input v-model="teacherForm.login" required placeholder="aliustoz" /></label>
              <label>Parol<input v-model="teacherForm.parol" required placeholder="123456" /></label>
              <label>Telefon<input v-model="teacherForm.phone" placeholder="+99890..." /></label>
              <label>Fan<input v-model="teacherForm.subject" placeholder="English" /></label>
              <button class="primary-btn">Ustozni saqlash</button>
            </form>
          </article>

          <article class="panel-card">
            <h3>Ustozlar ro‘yxati</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Ism</th><th>Login</th><th>Fan</th><th>Telefon</th><th>Amal</th></tr></thead>
                <tbody>
                  <tr v-for="teacher in teachers" :key="teacher.id">
                    <td>{{ teacher.full_name }}</td>
                    <td>{{ teacher.username }}</td>
                    <td>{{ teacher.subject || '-' }}</td>
                    <td>{{ teacher.phone || '-' }}</td>
                    <td><button class="danger-btn" @click="deleteTeacher(teacher.id)">O‘chirish</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section v-if="activeTab === 'classrooms'" class="page-section">
          <article class="panel-card">
            <h3>Sinf yaratish</h3>
            <form class="wide-form" @submit.prevent="createClassroom">
              <label v-if="isAdminLike">Ustoz
                <select v-model="classroomForm.teacher" required>
                  <option value="" disabled>Ustoz tanlang</option>
                  <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.full_name || teacher.username }}</option>
                </select>
              </label>
              <label>Sinf nomi<input v-model="classroomForm.name" required placeholder="9-A yoki 10-B" /></label>
              <label>Xona<input v-model="classroomForm.room" placeholder="101-xona" /></label>
              <label>Dars vaqti<input v-model="classroomForm.lesson_time" placeholder="08:00-10:00" /></label>
              <label>Ertalab yoki abetdan keyin
                <select v-model="classroomForm.shift">
                  <option value="morning">Ertalab</option>
                  <option value="afternoon">Abetdan keyin</option>
                </select>
              </label>
              <button class="primary-btn">Sinfni saqlash</button>
            </form>
          </article>

          <div class="cards-grid">
            <article v-for="classroom in classrooms" :key="classroom.id" class="class-card">
              <div class="tag">{{ shiftText(classroom.shift) }}</div>
              <h3>{{ classroom.name }}</h3>
              <div class="mini-grid">
                <span><b>Xona:</b> {{ classroom.room || '-' }}</span>
                <span><b>Dars:</b> {{ classroom.lesson_time || '-' }}</span>
                <span><b>Ustoz:</b> {{ classroom.teacher_detail?.full_name || classroom.teacher_name || '-' }}</span>
                <span><b>O‘quvchi:</b> {{ classroom.student_count }}</span>
              </div>
            </article>
          </div>
        </section>

        <section v-if="activeTab === 'students'" class="page-section">
          <article v-if="!canCreateStudent" class="panel-card warning-card">
            <h3>Director uchun cheklov</h3>
            <p>Director o‘quvchi yaratmaydi. Bu bo‘limda faqat o‘quvchilarni ko‘radi, sinf/ustoz bo‘yicha nazorat qiladi va Excel yuklaydi.</p>
          </article>

          <article v-if="canCreateStudent" class="panel-card">
            <h3>O‘quvchi qo‘shish</h3>
            <form class="student-form" @submit.prevent="createStudent">
              <label>Qaysi sinfga biriktiriladi
                <select v-model="studentForm.classroom" required>
                  <option value="" disabled>Sinf tanlang</option>
                  <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name || classroom.room }} — {{ classroom.teacher_name || classroom.teacher_detail?.full_name || 'ustoz yo‘q' }} — {{ classroom.lesson_time || 'vaqt yo‘q' }}</option>
                </select>
              </label>
              <label>Ism familyasi<input v-model="studentForm.full_name_input" required placeholder="Valiyev Ali" /></label>
              <label>Tug‘ilgan sana<input v-model="studentForm.birth_date" type="date" /></label>
              <label>Jinsi
                <select v-model="studentForm.gender">
                  <option value="male">Erkak</option>
                  <option value="female">Ayol</option>
                </select>
              </label>
              <label>O‘quvchi nomeri<input v-model="studentForm.phone_primary" placeholder="+99890..." /></label>
              <label>Otasining ism familyasi<input v-model="studentForm.father_full_name" placeholder="Valiyev Vali" /></label>
              <label>Otasining nomeri<input v-model="studentForm.father_phone" placeholder="+99890..." /></label>
              <label>Onasining ism familyasi<input v-model="studentForm.mother_full_name" placeholder="Valiyeva Malika" /></label>
              <label>Onasining nomeri<input v-model="studentForm.mother_phone" placeholder="+99890..." /></label>
              <label class="full-line">Manzil<input v-model="studentForm.address" placeholder="Toshkent viloyati, mahalla, uy" /></label>
              <button class="primary-btn">O‘quvchini saqlash</button>
            </form>
          </article>

          <article class="panel-card">
            <div class="section-head">
              <div>
                <h3>O‘quvchilar</h3>
                <p v-if="isAdminLike">Barcha o‘quvchilar ma’lumotlarini shu yerdan Excelga yuklab olishingiz mumkin.</p>
              </div>
              <div class="student-section-actions">
                <div class="filters">
                  <select v-model="filterClassroom">
                    <option value="">Barcha sinflar</option>
                    <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name || classroom.room }} — {{ classroom.teacher_name || classroom.teacher_detail?.full_name || 'ustoz yo‘q' }}</option>
                  </select>
                  <input v-model="searchText" placeholder="Qidirish..." />
                </div>
                <button v-if="isAdminLike" class="primary-btn" @click="downloadStudentsExcel">Excel yuklash</button>
              </div>
            </div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Ism familyasi</th><th>Tug‘ilgan sana</th><th>Sinf</th><th>Jinsi</th><th>Nomeri</th><th>Ota</th><th>Ona</th><th>Manzil</th></tr></thead>
                <tbody>
                  <tr v-for="student in filteredStudents" :key="student.id">
                    <td>{{ student.full_name }}</td>
                    <td>{{ formatDate(student.birth_date) }}</td>
                    <td>{{ student.classroom_name }}</td>
                    <td>{{ student.gender_display }}</td>
                    <td>{{ student.phone_primary || '-' }}</td>
                    <td>{{ student.father_full_name }}<br><small>{{ student.father_phone }}</small></td>
                    <td>{{ student.mother_full_name }}<br><small>{{ student.mother_phone }}</small></td>
                    <td>{{ student.address || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section v-if="activeTab === 'malumotlar'" class="page-section">
          <article class="panel-card hero-card">
            <div>
              <h3>Ma’lumotlar</h3>
              <p v-if="isAdminLike">Director/Admin barcha sinflar va barcha o‘quvchilar ma’lumotlarini ko‘radi.</p>
              <p v-else>Ustoz faqat o‘ziga biriktirilgan sinflar o‘quvchilarini ko‘radi.</p>
              <b>Jami: {{ malumotlar.total_students || 0 }} o‘quvchi, {{ malumotlar.total_classrooms || 0 }} sinf</b>
            </div>
            <button class="primary-btn" @click="downloadExcel">Excel formatda yuklash</button>
          </article>

          <article class="panel-card">
            <div class="section-head">
              <div>
                <h3>Barcha o‘quvchilar ma’lumotlari</h3>
                <p>Sinflar card bo‘lib ajratilmaydi — hamma o‘quvchi bitta uzun jadvalda ko‘rinadi.</p>
              </div>
              <div class="filters wide-filters">
                <select v-model="malumotlarClassroom">
                  <option value="">Barcha sinflar</option>
                  <option v-for="classroom in malumotlar.classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name || classroom.room }} — {{ classroom.teacher_name || 'ustoz yo‘q' }}</option>
                </select>
                <select v-model="malumotlarGender">
                  <option value="">Barcha jinslar</option>
                  <option value="male">Erkak</option>
                  <option value="female">Ayol</option>
                </select>
                <input v-model="malumotlarSearch" placeholder="Ism, telefon, ustoz, manzil bo‘yicha qidirish..." />
              </div>
            </div>
            <div class="stats-grid compact-stats malumotlar-counts">
              <article class="stat-card"><span>Tanlangan sinf</span><strong>{{ selectedMalumotlarClassroom?.name || 'Barchasi' }}</strong><small>{{ selectedMalumotlarClassroom?.teacher_name || 'Hamma ustozlar' }}</small></article>
              <article class="stat-card"><span>Shu sinfda</span><strong>{{ selectedMalumotlarClassroomTotal }}</strong><small>Jami o‘quvchi</small></article>
              <article class="stat-card"><span>Filter natijasi</span><strong>{{ filteredMalumotlarStudents.length }}</strong><small>Qidiruv/jins filteridan keyin</small></article>
            </div>
            <p class="muted-line">Ko‘rsatilmoqda: <b>{{ filteredMalumotlarStudents.length }}</b> ta o‘quvchi</p>
            <div class="table-wrap">
              <table class="wide-table">
                <thead>
                  <tr>
                    <th>№</th>
                    <th>O‘quvchi</th>
                    <th>Tug‘ilgan sana</th>
                    <th>Sinf</th>
                    <th>Ustoz</th>
                    <th>Jinsi</th>
                    <th>O‘quvchi nomeri</th>
                    <th>Ota</th>
                    <th>Ona</th>
                    <th>Manzil</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in filteredMalumotlarStudents" :key="student.id">
                    <td>{{ index + 1 }}</td>
                    <td><b>{{ student.full_name }}</b></td>
                    <td>{{ formatDate(student.birth_date) }}</td>
                    <td>{{ student.classroom_name || '-' }}</td>
                    <td>{{ student.teacher_name || '-' }}</td>
                    <td>{{ student.gender_display || '-' }}</td>
                    <td>{{ student.phone_primary || '-' }}</td>
                    <td>{{ student.father_full_name || '-' }}<br><small>{{ student.father_phone || '-' }}</small></td>
                    <td>{{ student.mother_full_name || '-' }}<br><small>{{ student.mother_phone || '-' }}</small></td>
                    <td>{{ student.address || '-' }}</td>
                  </tr>
                  <tr v-if="!filteredMalumotlarStudents.length">
                    <td colspan="10">Ma’lumot topilmadi</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section v-if="activeTab === 'today-absent'" class="page-section">
          <article class="panel-card hero-card">
            <div>
              <h3>Bugun kelmaganlar</h3>
              <p v-if="isAdminLike">Director/Admin barcha sinflar bo‘yicha bugun kelmagan o‘quvchilarni va umumiy sonlarni ko‘radi.</p>
              <p v-else>Ustoz faqat o‘ziga biriktirilgan sinflardagi bugun kelmagan o‘quvchilarni ko‘radi.</p>
              <b>Sana: {{ formatDate(todayAbsentReport.selected_date || new Date().toISOString()) }} · {{ todayAbsentReport.selected_weekday || dayName(new Date().toISOString()) }}</b>
            </div>
            <div class="action-row">
              <button class="primary-btn" @click="downloadTodayAbsentExcel">Excel yuklash</button>
              <button class="ghost-btn" @click="loadTodayAbsentReport">Yangilash</button>
            </div>
          </article>

          <article class="panel-card">
            <div class="section-head">
              <div>
                <h3>Umumiy hisob</h3>
                <p v-if="isAdminLike">Barcha sinflar kesimida bugungi kelmaganlar statistikasi.</p>
                <p v-else>Sizning sinflaringiz kesimida bugungi kelmaganlar statistikasi.</p>
              </div>
              <div class="filters">
                <select v-model="todayAbsentClassroom">
                  <option value="">Barcha sinflar</option>
                  <option v-for="classroom in todayAbsentReport.classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name }} — {{ classroom.teacher_name }}</option>
                </select>
              </div>
            </div>

            <div class="stats-grid compact-stats">
              <article class="stat-card"><span>Sinflar</span><strong>{{ todayAbsentFilteredSummary.total_classrooms }}</strong><small>Filter bo‘yicha</small></article>
              <article class="stat-card"><span>Jami o‘quvchi</span><strong>{{ todayAbsentFilteredSummary.total_students }}</strong><small>Shu sinflarda</small></article>
              <article class="stat-card danger-stat"><span>Jami kelmagan</span><strong>{{ todayAbsentFilteredSummary.total_absent_count }}</strong><small>Sababli + sababsiz</small></article>
              <article class="stat-card"><span>Sababsiz</span><strong>{{ todayAbsentFilteredSummary.unexcused_absent_count }}</strong><small>Kelmadi</small></article>
              <article class="stat-card"><span>Sababli</span><strong>{{ todayAbsentFilteredSummary.excused_count }}</strong><small>Sababli kelmagan</small></article>
              <article class="stat-card"><span>Belgilanmagan</span><strong>{{ todayAbsentFilteredSummary.not_marked_count }}</strong><small>Davomat qilinmagan</small></article>
            </div>
          </article>

          <article class="panel-card">
            <h3>Sinflar bo‘yicha kelmaganlar</h3>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Sinf</th>
                    <th>Ustozi</th>
                    <th>O‘quvchi</th>
                    <th>Keldi</th>
                    <th>Kech keldi</th>
                    <th>Sababsiz</th>
                    <th>Sababli</th>
                    <th>Jami kelmagan</th>
                    <th>Davomat qilinmagan</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="classroom in todayAbsentClassrooms" :key="classroom.id">
                    <td><b>{{ classroom.name }}</b><br><small>{{ classroom.lesson_time || '-' }} · {{ classroom.room || '-' }}</small></td>
                    <td>{{ classroom.teacher_name }}</td>
                    <td>{{ classroom.student_count }}</td>
                    <td>{{ classroom.present_count }}</td>
                    <td>{{ classroom.late_count }}</td>
                    <td>{{ classroom.unexcused_absent_count }}</td>
                    <td>{{ classroom.excused_count }}</td>
                    <td><b>{{ classroom.total_absent_count }}</b></td>
                    <td>{{ classroom.not_marked_count }}</td>
                  </tr>
                  <tr v-if="!todayAbsentClassrooms.length">
                    <td colspan="9">Bugun uchun sinf ma’lumoti topilmadi</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>

          <article class="panel-card">
            <div class="section-head">
              <div>
                <h3>Kelmagan o‘quvchilar ma’lumotlari</h3>
                <p>Bu yerda faqat “Kelmadi” va “Sababli” deb belgilangan o‘quvchilar chiqadi.</p>
              </div>
              <b class="count-badge">{{ todayAbsentStudents.length }} ta o‘quvchi</b>
            </div>
            <div class="table-wrap">
              <table class="wide-table">
                <thead>
                  <tr>
                    <th>№</th>
                    <th>O‘quvchi</th>
                    <th>Sinf</th>
                    <th>Ustoz</th>
                    <th>Holat</th>
                    <th>Sabab/izoh</th>
                    <th>O‘quvchi nomeri</th>
                    <th>Ota</th>
                    <th>Ona</th>
                    <th>Manzil</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(student, index) in todayAbsentStudents" :key="`${student.id}-${student.date}`">
                    <td>{{ index + 1 }}</td>
                    <td><b>{{ student.full_name }}</b></td>
                    <td>{{ student.classroom_name }}</td>
                    <td>{{ student.teacher_name }}</td>
                    <td><span :class="['status-pill', student.status_key]">{{ student.status }}</span></td>
                    <td>{{ student.reason || student.note || '-' }}</td>
                    <td>{{ student.phone_primary || '-' }}</td>
                    <td>{{ student.father_full_name || student.parent_name || '-' }}<br><small>{{ student.father_phone || '-' }}</small></td>
                    <td>{{ student.mother_full_name || '-' }}<br><small>{{ student.mother_phone || '-' }}</small></td>
                    <td>{{ student.address || '-' }}</td>
                  </tr>
                  <tr v-if="!todayAbsentStudents.length">
                    <td colspan="10">Bugun kelmagan o‘quvchi topilmadi</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section v-if="activeTab === 'attendance'" class="page-section">
          <article class="panel-card absent-preview-card">
            <div class="absent-preview-main">
              <div>
                <h3>Bugun kelmaganlar</h3>
                <p>Davomat bo‘limida bugun kelmagan o‘quvchilar, sabablar, sinfi va ota-onasi ma’lumotlari alohida turadi.</p>
              </div>
              <div class="absent-preview-stats">
                <span>Jami kelmagan</span>
                <strong>{{ todayAbsentFilteredSummary.total_absent_count }}</strong>
                <small>Sababli + sababsiz</small>
              </div>
            </div>
            <div class="action-row">
              <button class="primary-btn" @click="activeTab = 'today-absent'">To‘liq ko‘rish</button>
              <button class="ghost-btn" @click="downloadTodayAbsentExcel">Kelmaganlarni Excel yuklash</button>
            </div>
          </article>

          <article class="panel-card hero-card">
            <div>
              <h3>Kunlik o‘quvchi davomati</h3>
              <p>Ustoz har kuni o‘quvchilarga Keldi, Kelmadi, Sababli yoki Kech keldi holatini belgilaydi. Director kun va sinf bo‘yicha telefon raqamlari bilan nazorat qiladi.</p>
            </div>
            <div class="action-row">
              <button class="ghost-btn" @click="loadAttendanceReport">Hisobotni yangilash</button>
              <button class="primary-btn" @click="downloadAttendanceExcel">Excelga yuklash</button>
            </div>
          </article>

          <article class="panel-card">
            <div class="wide-form small-form">
              <label>Kun
                <input v-model="attendanceFilter.date" type="date" @change="loadAttendanceReport" />
              </label>
              <label>Sinf filter
                <select v-model="attendanceFilter.classroom" @change="loadAttendanceReport">
                  <option value="">Barcha sinflar</option>
                  <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name || classroom.room }} — {{ classroom.teacher_name || classroom.teacher_detail?.full_name || 'ustoz yo‘q' }}</option>
                </select>
              </label>
              <div class="weekday-card">{{ dayName(attendanceFilter.date) }}</div>
            </div>
          </article>

          <div class="stats-grid compact-stats">
            <article class="stat-card"><span>Jami o‘quvchi</span><strong>{{ attendanceReport.school_summary?.total_students || 0 }}</strong><small>Tanlangan kunda</small></article>
            <article class="stat-card"><span>Keldi</span><strong>{{ attendanceReport.school_summary?.present_count || 0 }}</strong><small>O‘z vaqtida kelgan</small></article>
            <article class="stat-card"><span>Kech keldi</span><strong>{{ attendanceReport.school_summary?.late_count || 0 }}</strong><small>Kech kelganlar</small></article>
            <article class="stat-card"><span>Jami kelmagan</span><strong>{{ attendanceReport.school_summary?.total_absent_count || 0 }}</strong><small>Sababli + sababsiz</small></article>
            <article class="stat-card"><span>Sababsiz</span><strong>{{ attendanceReport.school_summary?.unexcused_absent_count || 0 }}</strong><small>Kelmadi</small></article>
            <article class="stat-card"><span>Sababli</span><strong>{{ attendanceReport.school_summary?.excused_count || 0 }}</strong><small>Sababli</small></article>
          </div>

          <article class="panel-card">
            <h3>Sinflar bo‘yicha nazorat</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Sinf</th><th>Ustozi</th><th>O‘quvchi</th><th>Keldi</th><th>Kech keldi</th><th>Sababsiz</th><th>Sababli</th><th>Jami kelmagan</th><th>Davomat qilinmagan</th></tr></thead>
                <tbody>
                  <tr v-for="classroom in attendanceReport.classrooms" :key="classroom.id">
                    <td><b>{{ classroom.name }}</b><br><small>{{ classroom.lesson_time || '-' }} · {{ classroom.room || '-' }}</small></td>
                    <td>{{ classroom.teacher_name }}</td>
                    <td>{{ classroom.student_count }}</td>
                    <td>{{ classroom.present_count }}</td>
                    <td>{{ classroom.late_count }}</td>
                    <td>{{ classroom.unexcused_absent_count }}</td>
                    <td>{{ classroom.excused_count }}</td>
                    <td><b>{{ classroom.total_absent_count }}</b></td>
                    <td>{{ classroom.not_marked_count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>

          <article class="panel-card">
            <h3>Kunlik o‘quvchilar ro‘yxati — telefon raqamlari bilan</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>O‘quvchi</th><th>Sinf</th><th>Ustozi</th><th>Holat</th><th>Sabab/izoh</th><th>O‘quvchi nomeri</th><th>Ota nomeri</th><th>Ona nomeri</th></tr></thead>
                <tbody>
                  <tr v-for="student in attendanceReport.students" :key="`${student.id}-${student.date}`">
                    <td>{{ student.full_name }}</td>
                    <td>{{ student.classroom_name }}</td>
                    <td>{{ student.teacher_name }}</td>
                    <td><span :class="['status-pill', student.status_key]">{{ student.status }}</span></td>
                    <td>{{ student.reason || student.note || '-' }}</td>
                    <td>{{ student.phone_primary || '-' }}</td>
                    <td>{{ student.father_phone || '-' }}</td>
                    <td>{{ student.mother_phone || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>

          <template v-if="canEnterAttendance">
            <article class="panel-card">
              <h3>Davomat kiritish</h3>
              <p>Har kuni sinfni tanlab, har bir o‘quvchi uchun Keldi / Kelmadi / Sababli / Kech keldi holatini belgilang.</p>
              <div class="wide-form small-form">
                <label>Sinf
                  <select v-model="attendanceForm.classroom_id" required @change="attendanceFilter.classroom = attendanceForm.classroom_id; attendanceFilter.date = attendanceForm.date; loadAttendanceReport()">
                    <option value="" disabled>Sinf tanlang</option>
                    <option v-for="classroom in classrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name || classroom.room }} — {{ classroom.teacher_name || classroom.teacher_detail?.full_name || 'ustoz yo‘q' }}</option>
                  </select>
                </label>
                <label>Sana<input v-model="attendanceForm.date" type="date" @change="attendanceFilter.date = attendanceForm.date; attendanceFilter.classroom = attendanceForm.classroom_id; loadAttendanceReport()" /></label>
                <div class="weekday-card">{{ dayName(attendanceForm.date) }}</div>
              </div>
            </article>

            <article v-if="selectedAttendanceClass" class="panel-card">
              <h3>{{ selectedAttendanceClass.name }} — {{ selectedAttendanceClass.lesson_time }}</h3>
              <div class="attendance-list">
                <div v-for="student in selectedAttendanceStudents" :key="student.id" class="attendance-row">
                  <b>{{ student.full_name }}</b>
                  <div class="status-buttons">
                    <button :class="{ selected: attendanceForm.records[student.id]?.status === 'present' || !attendanceForm.records[student.id] }" @click="setAttendanceStatus(student.id, 'present')">Keldi</button>
                    <button :class="{ selected: attendanceForm.records[student.id]?.status === 'absent' }" @click="setAttendanceStatus(student.id, 'absent')">Kelmadi</button>
                    <button :class="{ selected: attendanceForm.records[student.id]?.status === 'late' }" @click="setAttendanceStatus(student.id, 'late')">Kech keldi</button>
                    <button :class="{ selected: attendanceForm.records[student.id]?.status === 'excused' }" @click="setAttendanceStatus(student.id, 'excused')">Sababli</button>
                  </div>
                  <input placeholder="Sabab yoki izoh" :value="attendanceForm.records[student.id]?.note || ''" @input="setAttendanceNote(student.id, $event.target.value)" />
                </div>
              </div>
              <button class="primary-btn" @click="saveAttendance">Davomatni saqlash</button>
            </article>
          </template>
        </section>

        <section v-if="activeTab === 'teacher-attendance' && isAdminLike" class="page-section">
          <article class="panel-card hero-card">
            <div>
              <h3>Ustozlar davomati nazorati</h3>
              <p>Director ustozlarning qaysi kuni nechida kelgani, nechida ketgani va qancha ishlaganini nazorat qiladi.</p>
            </div>
            <div class="action-row">
              <button class="ghost-btn" @click="loadTeacherAttendanceReport">Yangilash</button>
              <button class="primary-btn" @click="downloadTeacherAttendanceExcel">Excelga yuklash</button>
            </div>
          </article>

          <article class="panel-card">
            <div class="wide-form small-form">
              <label>Boshlanish sanasi
                <input v-model="teacherAttendanceFilter.start_date" type="date" @change="loadTeacherAttendanceReport" />
              </label>
              <label>Tugash sanasi
                <input v-model="teacherAttendanceFilter.end_date" type="date" @change="loadTeacherAttendanceReport" />
              </label>
              <label>Ustoz filter
                <select v-model="teacherAttendanceFilter.teacher" @change="loadTeacherAttendanceReport">
                  <option value="">Barcha ustozlar</option>
                  <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.full_name || teacher.username }}</option>
                </select>
              </label>
            </div>
          </article>

          <div class="stats-grid compact-stats">
            <article class="stat-card"><span>Ustozlar</span><strong>{{ teacherAttendanceReport.summary?.total_teachers || 0 }}</strong><small>Filter bo‘yicha</small></article>
            <article class="stat-card"><span>Kelgan</span><strong>{{ teacherAttendanceReport.summary?.present_count || 0 }}</strong><small>Check-in qilingan</small></article>
            <article class="stat-card"><span>Ketim bosgan</span><strong>{{ teacherAttendanceReport.summary?.checked_out_count || 0 }}</strong><small>Check-out qilingan</small></article>
            <article class="stat-card"><span>Jami ishlagan</span><strong>{{ teacherAttendanceReport.summary?.worked_label_total || '0 soat 0 daqiqa' }}</strong><small>Tanlangan oraliq</small></article>
          </div>

          <article class="panel-card">
            <h3>Ustozlar kelish-ketish ro‘yxati</h3>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Ustoz ism familyasi</th>
                    <th>Sana</th>
                    <th>Soat nechida kelgan</th>
                    <th>Soat nechida ketgan</th>
                    <th>Qancha ishlagan</th>
                    <th>Holat</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in teacherAttendanceReport.rows" :key="`${row.teacher}-${row.date}`">
                    <td><b>{{ row.teacher_name }}</b><br><small>{{ row.subject || row.classrooms || '-' }}</small></td>
                    <td>{{ row.date_label }}</td>
                    <td>{{ row.check_in_time || '-' }}</td>
                    <td>{{ row.check_out_time || '-' }}</td>
                    <td>{{ row.worked_label }}</td>
                    <td>
                      {{ row.status }}
                      <small v-if="row.is_late"> · kechikdi</small>
                      <small v-if="row.left_early"> · erta ketdi</small>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </section>


      </section>
    </section>
  </main>
</template>
