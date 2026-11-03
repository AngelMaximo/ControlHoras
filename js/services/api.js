import { API_BASE_URL } from "../config/settings.js";

export async function requestApi(path, { method = "GET", body, signal } = {}) {
	if (!API_BASE_URL) {
		throw new Error("La URL de la API todavía no está configurada.");
	}

	const baseUrl = `${API_BASE_URL.replace(/\/+$/, "")}/`;
	const endpoint = new URL(String(path).replace(/^\/+/, ""), baseUrl);
	const headers = { Accept: "application/json" };
	const options = {
		method,
		headers,
		credentials: "include",
		signal,
	};

	if (body !== undefined) {
		headers["Content-Type"] = "application/json";
		options.body = JSON.stringify(body);
	}

	const response = await fetch(endpoint, options);

	if (response.status === 204) {
		return null;
	}

	const responseBody = await response.json().catch(() => null);

	if (!response.ok) {
		throw new Error(responseBody?.detail ?? "No se pudo completar la solicitud.");
	}

	return responseBody;
}
