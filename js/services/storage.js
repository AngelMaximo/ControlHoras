import { STORAGE_KEY } from "../config/settings.js";
import { normalizeEmployeeName } from "../utils/validation.js";

export function loadWorkdays() {
	const savedRecords = localStorage.getItem(STORAGE_KEY);

	if (!savedRecords) {
		return [];
	}

	const records = JSON.parse(savedRecords);

	if (!Array.isArray(records)) {
		throw new Error("Los registros guardados tienen un formato inválido.");
	}

	return records;
}

export function saveWorkday(workday) {
	const records = loadWorkdays();
	const recordIndex = records.findIndex((record) => record.id === workday.id);

	if (recordIndex === -1) {
		records.push(workday);
	} else {
		records[recordIndex] = workday;
	}

	localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
	return workday;
}

export function findWorkdayForEmployee(workDate, employeeName) {
	const normalizedName = normalizeEmployeeName(employeeName);

	return loadWorkdays().find((workday) => (
		workday.workDate === workDate
		&& normalizeEmployeeName(workday.employee.name) === normalizedName
	)) ?? null;
}

export function findOpenWorkday() {
	return loadWorkdays()
		.filter((workday) => !workday.clockOut)
		.sort((first, second) => new Date(second.clockIn) - new Date(first.clockIn))[0] ?? null;
}
