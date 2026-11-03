const clockFormatter = new Intl.DateTimeFormat("es-MX", {
	hour: "2-digit",
	minute: "2-digit",
	hourCycle: "h23",
});

const dateFormatter = new Intl.DateTimeFormat("es-MX", {
	dateStyle: "full",
});

function padNumber(value) {
	return String(value).padStart(2, "0");
}

export function getLocalDateKey(date = new Date()) {
	return [
		date.getFullYear(),
		padNumber(date.getMonth() + 1),
		padNumber(date.getDate()),
	].join("-");
}

export function formatDate(date = new Date()) {
	return dateFormatter.format(date);
}

export function formatTime(value) {
	if (!value) {
		return "--:--";
	}

	const date = value instanceof Date ? value : new Date(value);
	return Number.isNaN(date.getTime()) ? "--:--" : clockFormatter.format(date);
}

export function formatDuration(milliseconds) {
	const totalMinutes = Math.max(0, Math.floor(milliseconds / 60_000));
	const hours = Math.floor(totalMinutes / 60);
	const minutes = totalMinutes % 60;

	if (hours === 0) {
		return `${minutes} min`;
	}

	return `${hours} h ${padNumber(minutes)} min`;
}

export function getBreakDuration(workday, now = new Date()) {
	if (!workday?.breakStart) {
		return null;
	}

	const end = workday.breakEnd ? new Date(workday.breakEnd) : now;
	const start = new Date(workday.breakStart);
	return Math.max(0, end.getTime() - start.getTime());
}
