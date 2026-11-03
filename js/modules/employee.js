import { validateEmployeeInput } from "../utils/validation.js";

export function createEmployee(name, type) {
	const result = validateEmployeeInput(name, type);

	if (!result.valid) {
		throw new Error(result.message);
	}

	return result.employee;
}

export function getEmployeeTypeLabel(type) {
	return type === "temporary" ? "Temporal" : "Permanente";
}
