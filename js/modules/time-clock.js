import { getLocalDateKey } from "../utils/date-time.js";

function createId() {
	if (globalThis.crypto?.randomUUID) {
		return globalThis.crypto.randomUUID();
	}

	return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createWorkday(employee, now = new Date()) {
	return {
		id: createId(),
		workDate: getLocalDateKey(now),
		employee: { ...employee },
		clockIn: now.toISOString(),
		breakStart: null,
		breakEnd: null,
		clockOut: null,
	};
}

export function getWorkdayState(workday) {
	if (!workday) {
		return "not-started";
	}

	if (workday.clockOut) {
		return "completed";
	}

	if (workday.breakStart && !workday.breakEnd) {
		return "on-break";
	}

	if (workday.breakEnd) {
		return "break-complete";
	}

	return "working";
}

export function recordClockOut(workday, now = new Date()) {
	const state = getWorkdayState(workday);

	if (state === "on-break") {
		throw new Error("Finaliza el descanso antes de registrar la salida.");
	}

	if (state !== "working" && state !== "break-complete") {
		throw new Error("No hay una jornada activa para finalizar.");
	}

	return { ...workday, clockOut: now.toISOString() };
}
