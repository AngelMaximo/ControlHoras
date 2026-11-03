from server.database.workdays import employee_exit
from server.database.workdays import employee_entrance
from server.database.employees import deactivate_employee
from server.database.breaks import start_break
from server.database.breaks import end_break

#INICIAR DESCANSO
"""workday_id = "72b53089-1bc1-4db6-849d-28d481aa5671"
break_id = start_break(workday_id)
print("ID del descanso:",break_id)"""

#FINALIZAR DESCANSO
"""break_id = "581bac59-a74a-4d3b-a568-6748bd5302ed"
end_break_id = end_break(break_id)
print("ID del final del descanso:",end_break_id)"""

#INICIAR JORNADA
"""employee_id = 8
workday_id = employee_entrance(employee_id)
print("ID de la jornada:", workday_id)"""

#CERRRAR JORNADA
workday_id="72b53089-1bc1-4db6-849d-28d481aa5671"
employee_exit(workday_id)


