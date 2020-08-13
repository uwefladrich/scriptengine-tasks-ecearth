******************
Presentation Tasks
******************

Markdown Report
===============

Mapped to ``ece.mon.markdown_report``.

::

    - ece.mon.markdown_report
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/output-disk-usage.yml"
            - "{{mondir}}/tos-global-avg.nc"
            - "{{mondir}}/sos-global-avg.nc"
        dst: "{{mondir}}/report"
        template: "scriptengine-tasks-ecearth/docs/templates/monitoring.md.j2"

Redmine Output
==============

Mapped to ``ece.mon.redmine_output``.

::

    - ece.mon.redmine_output
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/sim-years.yml"
            - "{{mondir}}/tos-global-avg.nc"
            - "{{mondir}}/sos-global-avg.nc"
            - "{{mondir}}/sithic-north-mar.nc"
            - "{{mondir}}/sithic-north-sep.nc"
        local_dst: "{{mondir}}/redmine-report"
        api_key: # API key for the EC-Earth Dev Portal
        subject: "Monitored Experiment: {{exp_id}}"
        template: "scriptengine-tasks-ecearth/docs/templates/redmine_template.txt.j2"