const BASE_URL = '/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })
  const text = await res.text()
  const data = text ? JSON.parse(text) : null
  if (!res.ok) {
    throw new Error(data?.detail || `请求失败 (${res.status})`)
  }
  return data
}

function qs(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      search.set(k, String(v))
    }
  })
  const str = search.toString()
  return str ? `?${str}` : ''
}

export const api = {
  // Dashboard & Announcements
  getOverview: () => request('/dashboard/overview'),
  createAnnouncement: (payload) => request('/dashboard/announcements', { method: 'POST', body: JSON.stringify(payload) }),

  // Association (FR-AM)
  getApplications: (params) => request(`/association/applications${qs(params)}`),
  createApplication: (payload) => request('/association/applications', { method: 'POST', body: JSON.stringify(payload) }),
  reviewApplication: (id, payload) => request(`/association/applications/${id}/review`, { method: 'POST', body: JSON.stringify(payload) }),

  getMembers: (params) => request(`/association/members${qs(params)}`),
  createMember: (payload) => request('/association/members', { method: 'POST', body: JSON.stringify(payload) }),
  getMemberProfile: (id) => request(`/association/members/${id}`),
  promoteMember: (id, payload) => request(`/association/members/${id}/promote`, { method: 'POST', body: JSON.stringify(payload) }),
  changeMemberStatus: (id, payload) => request(`/association/members/${id}/status`, { method: 'POST', body: JSON.stringify(payload) }),

  getMemberAssessments: (params) => request(`/association/assessments${qs(params)}`),
  createMemberAssessment: (payload) => request('/association/assessments', { method: 'POST', body: JSON.stringify(payload) }),

  getPositions: () => request('/association/positions'),
  createPosition: (payload) => request('/association/positions', { method: 'POST', body: JSON.stringify(payload) }),

  getRewards: () => request('/association/rewards'),
  createReward: (payload) => request('/association/rewards', { method: 'POST', body: JSON.stringify(payload) }),

  // Question Bank (FR-QB)
  getTags: (params) => request(`/question-bank/tags${qs(params)}`),
  createTag: (payload) => request('/question-bank/tags', { method: 'POST', body: JSON.stringify(payload) }),

  getProblems: (params) => request(`/question-bank/problems${qs(params)}`),
  createProblem: (payload) => request('/question-bank/problems', { method: 'POST', body: JSON.stringify(payload) }),
  getProblemDetail: (id) => request(`/question-bank/problems/${id}`),
  deleteProblem: (id) => request(`/question-bank/problems/${id}`, { method: 'DELETE' }),
  addSolution: (problemId, payload) => request(`/question-bank/problems/${problemId}/solutions`, { method: 'POST', body: JSON.stringify(payload) }),

  getProblemLists: () => request('/question-bank/problem-lists'),
  createProblemList: (payload) => request('/question-bank/problem-lists', { method: 'POST', body: JSON.stringify(payload) }),
  getQuestionBankStats: () => request('/question-bank/stats'),

  // Ability Assessment (FR-AB)
  getAbilityAssessments: (params) => request(`/ability/assessments${qs(params)}`),
  createAbilityAssessment: (payload) => request('/ability/assessments', { method: 'POST', body: JSON.stringify(payload) }),
  getMemberAbilityProfile: (memberId) => request(`/ability/members/${memberId}/profile`)
}
