from __future__ import annotations

bl_info = {
    "name": "Render events webhooks",
    "author": "campfred",
    "version": (1, 1),
    "blender": (2, 93, 0),
    "location": "Render",
    "description": "Send webhooks to a server upon render events.",
    "doc_url": "",
    "category": "Render",
}

from enum import Enum
import json
import urllib.parse
import urllib.request
import urllib.error
import bpy


###
# Utilities
class RenderEvents(Enum):
    START = "start"
    PROGRESS = "progress"
    COMPLETE = "complete"
    CANCEL = "cancel"
    ERROR = "error"


def poke_webhook(event: RenderEvents, data: dict[str, str]) -> None:
    # Getting info on what webhook server to poke
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    base_url = addon_prefs.webhook_url
    path = getattr(addon_prefs, f"render_{event.value}_path")
    url = f"{base_url}{path}"

    frame_first = bpy.context.scene.frame_start
    frame_current = bpy.context.scene.frame_current
    frame_last = bpy.context.scene.frame_end
    frame_count = (
        frame_last - frame_first + 1
    )  # Using frame_start in case the first frame isn't #0

    # Prepping basic data about the render job
    job_data = {
        "project_name": bpy.path.basename(bpy.data.filepath),
        "output_name": bpy.path.basename(bpy.context.scene.render.filepath),
        "frame_count": frame_count,
    }
    # Prepping extra data about the render job's progress
    if event == RenderEvents.PROGRESS:
        job_data = job_data | {
            "progress": {
                "percent": int(
                    (frame_current - frame_first) / (frame_last - frame_first) * 100
                ),
                "frames": {
                    "index_first": frame_first,
                    "index_last": frame_last,
                    "index_current": frame_current,
                },
            }
        }
    # Adding the caller's extra data about the render job
    job_data = job_data | data

    try:
        print(
            f"Render event webhooks: Sending « PUT » request to {base_url}{path}. 📨 Data : ",
            job_data,
        )
        request = urllib.request.Request(
            url=url, data=json.dumps(job_data).encode("utf-8"), method="PUT"
        )
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                print(
                    f"Render event webhooks: Server notified succesfully of a render {event.value} event. 🎉"
                )
            else:
                print(
                    f"Render event webhooks: Webhook request failed with status code {response.status}. ❗ Response message : ",
                    {response.read().decode("utf-8")},
                )
    except urllib.error.HTTPError as error:
        print(
            f"Render event webhooks: Webhook request failed with code {error.code}. ❗ Response message : ",
            {error.read().decode("utf-8")},
        )
    except Exception as exception:
        print(
            "Render event webhooks: Error making the webhook request, exception happened. ❗ Exception : ",
            {exception},
        )


###
# Add-on preferences setup
class RenderWebhookAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    webhook_url: bpy.props.StringProperty(
        name="Webhook URL",
        description="The base URL of the webhook to call.",
        default="https://server.local/api/webhook",
    )  # type: ignore

    render_start_path: bpy.props.StringProperty(
        name="Render start path",
        description="The path to use for the webhook call when the render starts.",
        default="/render_start",
    )  # type: ignore

    render_progress_path: bpy.props.StringProperty(
        name="Render progress path",
        description="The path to use for the webhook call when the render progresses.",
        default="/render_progress",
    )  # type: ignore

    render_complete_path: bpy.props.StringProperty(
        name="Render complete path",
        description="The path to use for the webhook call when the render completes.",
        default="/render_complete",
    )  # type: ignore

    render_cancel_path: bpy.props.StringProperty(
        name="Render cancel path",
        description="The path to use for the webhook call when the render cancels.",
        default="/render_cancel",
    )  # type: ignore

    render_error_path: bpy.props.StringProperty(
        name="Render error path",
        description="The path to use for the webhook call when the render errors.",
        default="/render_error",
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.label(text="Please configure these settings for the add-on to work.")
        layout.prop(self, "webhook_url")
        for event in RenderEvents:
            layout.prop(self, f"render_{event.value}_path")


###
# Add-on actual actions
def render_start_handler(scene):
    """Update webhook about render start."""
    poke_webhook(event=RenderEvents.START, data={})


def render_progress_handler(scene):
    """Update webhook about render progression."""
    poke_webhook(event=RenderEvents.PROGRESS, data={})


def render_complete_handler(scene):
    """Update webhook about render completion."""
    poke_webhook(event=RenderEvents.COMPLETE, data={})


def render_cancel_handler(scene):
    """Update webhook about render cancellation."""
    # Get the error message from the Blender scene
    if scene.render.error_message:
        error_message = scene.render.error_message
        poke_webhook(event=RenderEvents.ERROR, data={"error_message": error_message})
    else:
        poke_webhook(event=RenderEvents.CANCEL, data={})


###
# Add-on registration
def register():
    bpy.utils.register_class(RenderWebhookAddonPreferences)
    bpy.app.handlers.render_init.append(render_start_handler)
    bpy.app.handlers.render_write.append(render_progress_handler)
    bpy.app.handlers.render_complete.append(render_complete_handler)
    bpy.app.handlers.render_cancel.append(render_cancel_handler)
    print("Render event webhooks: Registered. ✅ Bonjour!")


def unregister():
    bpy.utils.unregister_class(RenderWebhookAddonPreferences)
    bpy.app.handlers.render_init.remove(render_start_handler)
    bpy.app.handlers.render_write.remove(render_progress_handler)
    bpy.app.handlers.render_complete.remove(render_complete_handler)
    bpy.app.handlers.render_cancel.remove(render_cancel_handler)
    print("Render event webhooks: Deregistered. ✅ Goodbye!")


if __name__ == "__main__":
    register()
