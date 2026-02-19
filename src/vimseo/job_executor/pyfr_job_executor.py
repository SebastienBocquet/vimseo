from vimseo.job_executor.base_user_job_options import BaseUserJobSettings


class PyFRJobSettings(BaseUserJobSettings):
    """The user job options for PyFR."""

    backend: str = "openmp"

