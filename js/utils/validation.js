const EMPLOYEE_TYPES = new Set(["permanent", "temporary"]);
const EMPLOYEE_NAME_PATTERN = /^\p{L}+(?:\s+\p{L}+)*$/u;

export function isValidEmployeeName(name) {
	const cleanName = name.trim().replace(/\s+/g, " ");
	return EMPLOYEE_NAME_PATTERN.test(cleanName);
}

export function normalizeEmployeeName(name) {
	return name.trim().replace(/\s+/g, " ").toLocaleLowerCase("es-MX");
}

export function validateEmployeeInput(name, type) {
	const cleanName = name.trim().replace(/\s+/g, " ");

	if (cleanName.length < 2) {
		return { valid: false, message: "Escribe el nombre completo del empleado." };
	}

	if (cleanName.length > 100) {
		return { valid: false, message: "El nombre no puede superar 100 caracteres." };
	}

	if (!isValidEmployeeName(cleanName)) {
		return {
			valid: false,
			message: "El nombre solo puede contener letras y espacios.",
		};
	}

	if (!EMPLOYEE_TYPES.has(type)) {
		return { valid: false, message: "Selecciona el tipo de empleado." };
	}

	return {
		valid: true,
		employee: { name: cleanName, type },
	};
}
