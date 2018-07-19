# Datadog Observatory Integration

This is a [Datadog][] integration for fetching metrics from [Mozilla Observatory][] web service.

The code herein is a working integration, but requires more work to
make it eligible into inclusion to the [official Datadog integrations](https://docs.datadoghq.com/developers/integrations/new_check_howto/).

It is currently provided as-is, without any additional documentation or support.
Future work plans include writing sufficient documentation and fulfilling
requirements to submit it to the main Datadog repository.

## Usage

Requires an already installed Datadog Agent deployment.

- Copy `observatory.py` into `/etc/datadog-agent/checks.d/` folder
- Copy `observatory.yaml` into `/etc/datadog-agent/conf.d/` folder and change as needed


## License

Apache2 license

[Datadog]: https://datadoghq.com
[Mozilla Observatory]: https://observatory.mozilla.org
