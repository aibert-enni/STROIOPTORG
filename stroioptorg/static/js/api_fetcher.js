async function api(url, options = {}, retry = true) {
  const domain = "http://localhost:8000"

  options.credentials = 'include';  // Чтобы всегда шли куки

  const request_url = domain + url;

  let response = await fetch(request_url, options);

  if (response.status === 401 && retry) {
    // Пробуем рефрешнуть
    const refreshResponse = await fetch(domain + '/api/v1/auth/token/refresh/', {
      method: 'POST',
      credentials: 'include'
    });

    if (refreshResponse.ok) {
      // После успешного refresh, повторяем оригинальный запрос
      response = await fetch(request_url, options);
    } else {
      console.error('Refresh failed. Redirecting to login...');
      // Здесь можно редиректить на login
    }
  }

  return response;
}