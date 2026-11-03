import { createEmployee, getEmployeeTypeLabel } from "./modules/employee.js";
import { endBreak, startBreak } from "./modules/break.js";
import {
	createWorkday,
	getWorkdayState,
	recordClockOut,
} from "./modules/time-clock.js";
import {
	formatDate,
	formatDuration,
	formatTime,
	getBreakDuration,
	getLocalDateKey,
} from "./utils/date-time.js";
import {
	findOpenWorkday,
	findWorkdayForEmployee,
	saveWorkday,
} from "./services/storage.js";
import { isValidEmployeeName } from "./utils/validation.js";

const elements = {
	employeeForm: document.getElementById("employee-form"),
	employeeName: document.getElementById("employee-name"),
	employeeType: document.getElementById("employee-type"),
	clockInButton: document.getElementById("clock-in-button"),
	clockInTime: document.getElementById("clock-in-time"),
	breakStartTime: document.getElementById("break-start-time"),
	breakEndTime: document.getElementById("break-end-time"),
	clockOutTime: document.getElementById("clock-out-time"),
	breakDuration: document.getElementById("break-duration"),
	breakStartButton: document.getElementById("break-start-button"),
	breakEndButton: document.getElementById("break-end-button"),
	clockOutButton: document.getElementById("clock-out-button"),
	statusMessage: document.getElementById("status-message"),
	workdayDate: document.getElementById("workday-date"),
};

let currentWorkday = null;

function showMessage(message, isError = false) {
	elements.statusMessage.textContent = message;
	elements.statusMessage.setAttribute("role", isError ? "alert" : "status");
	elements.statusMessage.setAttribute("aria-live", isError ? "assertive" : "polite");
}

function renderWorkday() {
	const state = getWorkdayState(currentWorkday);
	const canRegister = state === "not-started" || state === "completed";

	elements.workdayDate.textContent = formatDate(new Date());
	elements.employeeName.value = currentWorkday?.employee.name ?? "";
	elements.employeeType.value = currentWorkday?.employee.type ?? "";
	elements.employeeName.disabled = !canRegister;
	elements.employeeType.disabled = !canRegister;
	elements.clockInButton.disabled = !canRegister;

	elements.clockInTime.textContent = formatTime(currentWorkday?.clockIn);
	elements.breakStartTime.textContent = formatTime(currentWorkday?.breakStart);
	elements.breakEndTime.textContent = formatTime(currentWorkday?.breakEnd);
	elements.clockOutTime.textContent = formatTime(currentWorkday?.clockOut);

	const breakDuration = getBreakDuration(currentWorkday);
	elements.breakDuration.textContent = breakDuration === null
		? "--"
		: formatDuration(breakDuration);

	elements.breakStartButton.disabled = state !== "working";
	elements.breakEndButton.disabled = state !== "on-break";
	elements.clockOutButton.disabled = state !== "working" && state !== "break-complete";
}

function persistWorkday(workday) {
	saveWorkday(workday);
	currentWorkday = workday;
	renderWorkday();
}

function handleEmployeeNameInput() {
	const name = elements.employeeName.value;
	const hasInvalidCharacters = name && !isValidEmployeeName(name);

	elements.employeeName.setCustomValidity(
		hasInvalidCharacters ? "El nombre solo puede contener letras y espacios." : "",
	);

	if (hasInvalidCharacters) {
		showMessage("El nombre solo puede contener letras y espacios.", true);
		return;
	}

	if (!name || isValidEmployeeName(name)) {
		showMessage("");
	}
}

function handleInvalidEmployeeName() {
	if (!elements.employeeName.value) {
		elements.employeeName.setCustomValidity("Por favor, completa el campo de nombre completo.");
		showMessage("Por favor, completa el campo de nombre completo.", true);
		return;
	}

	if (!isValidEmployeeName(elements.employeeName.value)) {
		elements.employeeName.setCustomValidity("El nombre solo puede contener letras y espacios.");
		showMessage("El nombre solo puede contener letras y espacios.", true);
	}
}

function handleEmployeeTypeChange() {
	elements.employeeType.setCustomValidity("");
}

function handleInvalidEmployeeType() {
	elements.employeeType.setCustomValidity("Por favor, selecciona un tipo de empleado de la lista.");
	showMessage("Por favor, selecciona un tipo de empleado de la lista.", true);
}

function handleEmployeeSubmit(event) {
	event.preventDefault();

	try {
		const employee = createEmployee(
			elements.employeeName.value,
			elements.employeeType.value,
		);
		const today = getLocalDateKey();
		const existingWorkday = findWorkdayForEmployee(today, employee.name);

		if (existingWorkday) {
			currentWorkday = existingWorkday;
			renderWorkday();
			showMessage("Este empleado ya tiene un registro de jornada para hoy.", true);
			return;
		}

		const openWorkday = findOpenWorkday();

		if (openWorkday) {
			currentWorkday = openWorkday;
			renderWorkday();
			showMessage("Hay otra jornada activa en este navegador. Finalízala primero.", true);
			return;
		}

		const workday = createWorkday(employee);
		persistWorkday(workday);
		showMessage(
			`Entrada registrada para ${employee.name} (${getEmployeeTypeLabel(employee.type)}) a las ${formatTime(workday.clockIn)}.`,
		);
	} catch (error) {
		showMessage(error.message || "No se pudo registrar la entrada.", true);
	}
}

function handleStartBreak() {
	try {
		persistWorkday(startBreak(currentWorkday));
		showMessage(`Descanso iniciado a las ${formatTime(currentWorkday.breakStart)}.`);
	} catch (error) {
		showMessage(error.message || "No se pudo iniciar el descanso.", true);
	}
}

function handleEndBreak() {
	const confirmed = window.confirm("¿Está seguro de que quiere finalizar el descanso?");

	if (!confirmed) {
		return;
	}

	try {
		persistWorkday(endBreak(currentWorkday));
		showMessage(`Descanso finalizado a las ${formatTime(currentWorkday.breakEnd)}.`);
	} catch (error) {
		showMessage(error.message || "No se pudo finalizar el descanso.", true);
	}
}

function handleClockOut() {
	const confirmed = window.confirm("¿Está seguro de que quiere registrar la salida?");

	if (!confirmed) {
		return;
	}

	try {
		persistWorkday(recordClockOut(currentWorkday));
		showMessage(`Salida registrada a las ${formatTime(currentWorkday.clockOut)}.`);
	} catch (error) {
		showMessage(error.message || "No se pudo registrar la salida.", true);
	}
}

function initialize() {
	elements.employeeForm.addEventListener("submit", handleEmployeeSubmit);
	elements.employeeName.addEventListener("input", handleEmployeeNameInput);
	elements.employeeName.addEventListener("invalid", handleInvalidEmployeeName);
	elements.employeeType.addEventListener("change", handleEmployeeTypeChange);
	elements.employeeType.addEventListener("invalid", handleInvalidEmployeeType);
	elements.breakStartButton.addEventListener("click", handleStartBreak);
	elements.breakEndButton.addEventListener("click", handleEndBreak);
	elements.clockOutButton.addEventListener("click", handleClockOut);

	try {
		currentWorkday = findOpenWorkday();
		renderWorkday();

		if (currentWorkday) {
			showMessage(`Jornada activa de ${currentWorkday.employee.name} restaurada.`);
		} else {
			showMessage("Los registros se guardan en este dispositivo.");
		}
	} catch (error) {
		renderWorkday();
		showMessage(error.message || "No se pudieron cargar los registros guardados.", true);
	}

	window.setInterval(() => {
		if (getWorkdayState(currentWorkday) === "on-break") {
			const breakDuration = getBreakDuration(currentWorkday);
			elements.breakDuration.textContent = formatDuration(breakDuration);
		}
	}, 30_000);
}

initialize();
