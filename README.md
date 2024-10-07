# Render events webhooks for Blender

This script allows to send webhook to servers (like Home Assistant in my use case) for notifying of render events in Blender.

## Supported events

- **Start**
  When a render started.
- **Progress**
- When a render progresses.
- **Complete**
  When a render completed.
- **Cancel**
  When a render is cancelled.
- **Error**
  This one doesn't actually exist in Blender's Python API.
  It's just guessed based on if there's an error message in the render's properties or not upon render cancellation.

## Installation

1. Download script ([`render_webhooks.py`](render_webhooks.py))
2. Open Blender's preferences (`Ctrl` + `,`)
3. Open the « Add-ons » page
4. Click the little down arrow 🔽 at the top right corner and select « Install from Disk... »
5. Open the script file ([`render_webhooks.py`](render_webhooks.py))
6. Set your Webhook URL and your paths
   > [!tip] Single webhook operation without paths
   > If you need only a single webhook address without different paths for each event, simply leave the paths empty and set your URL as the « Webhook URL ».
   > [!tip] Multiple different webhooks with no commonality between them
   > If you need to call completely different webhook addresses for each event, simply leave the « Webhook URL » empty and put the complete address for each even in their respective paths.

## Data to expect from incoming webhook calls

Webhook calls that will be made by this plugin will contain the following data in the request body.

| Field                           | Value                                                                   | Example              |
| ------------------------------- | ----------------------------------------------------------------------- | -------------------- |
| `project_name`                  | The project's file name.                                                | `TurntableAnimation` |
| `frame_count`                   | The number of frames to render.                                         | `240`                |
| `progress.percent`              | The percentage completed of the render job.                             | `46`                 |
| `progress.frames.index_first`   | The number of the first frame of the animation to render.               | `0`                  |
| `progress.frames.index_last`    | The number of the last frame of the animation to render.                | `239`                |
| `progress.frames.index_current` | The number of the currently rendering frame of the animation to render. | `111`                |

Here's an example of how it would look on the receiving end.

```json
{
  "project_name": "TurntableAnimation",
  "frame_count": 240, 
  "progress": {
    "percent": 46, // (index_current - index_first) / (index_last - index_first) * 100, rounded
    "frames": {
      "index_first": 0,
      "index_last" : 239,
      "index_current": 111 
    }
}
```
