******************
Presentation Tasks
******************

Markdown
===============

Mapped to ``ece.mon.presentation.markdown``.

::

    - ece.mon.presentation.markdown:
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/output-disk-usage.yml"
            - "{{mondir}}/tos-global-avg.nc"
            - "{{mondir}}/sos-global-avg.nc"
        dst: "{{mondir}}/report"
        template: "scriptengine-tasks-ecearth/docs/templates/monitoring.md.j2"

Custom Visualization Options
#############################

For custom visualization, a dictionary instead of the path alone can be passed as a source.
The path then must lie at the key ``path``.
Currently, the following customization features are implemented:

    * ``value_range``: set the minimum and maximum value of a time series or (temporal) map. Particularly useful for temporal maps. Default: ``[None, None]``
    * ``colormap``: set a custom colormap for maps and temporal maps. Default: ``RdBu_r``. The list of possible colormaps is in the `Matplotlib documentation <https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html>`

Example::

    - ece.mon.presentation.markdown
        src:
            - "{{mondir}}/description.yml"
            - "{{mondir}}/exp-id.yml"
            - "{{mondir}}/output-disk-usage.yml"
            - path: "full/path/to/tos_nemo_global_mean_year_mean_timeseries.nc"
              value_range: [13, 17]
            - path: "full/path/to/tos_nemo_year_mean_temporalmap.nc"
              value_range: [-2, 30]
              colormap: 'viridis'
        dst: "{{mondir}}/report"
        template: "scriptengine-tasks-ecearth/docs/templates/monitoring.md.j2"


Redmine
==============

Mapped to ``ece.mon.presentation.redmine``.

::

    - ece.mon.presentation.redmine:
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