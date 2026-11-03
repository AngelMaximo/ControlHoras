import { getWorkdayState } from "./time-clock.js";

export function startBreak(workday, now = new Date()) {
	if (getWorkdayState(workday) !== "working") {
		throw new Error("No se puede iniciar un descanso en este momento.");
	}

	return { ...workday, breakStart: now.toISOString() };
}

export function endBreak(workday, now = new Date()) {
	if (getWorkdayState(workday) !== "on-break") {
		throw new Error("No hay un descanso activo para finalizar.");
	}

	return { ...workday, breakEnd: now.toISOString() };
}
