// k6 smoke for auth send-code (adjust URL/host)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  const url = `${__ENV.BASE_URL || 'https://example.local'}/api/auth/phone/send-code`;
  const res = http.post(url, JSON.stringify({ phone: "+79990000000" }), {
    headers: { 'Content-Type': 'application/json' },
  });
  check(res, { 'status is 200 or 429': (r) => r.status === 200 || r.status === 429 });
  sleep(1);
}
