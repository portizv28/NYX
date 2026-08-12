from nyx import NYX
from integrations.windows.tray import WindowsTrayIntegration

app = NYX()
tray = WindowsTrayIntegration(
    open_center=app.request_open_control_center,
    toggle_listening=app.request_toggle_listening,
    shutdown=app.request_shutdown,
    status=app.status_text,
)

tray.start()
try:
    app.run()
finally:
    tray.stop()




