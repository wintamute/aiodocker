import json
from typing import Optional, Dict, List, Any
from .utils import clean_config, clean_networks, clean_filters, format_env


class DockerServices(object):
    def __init__(self, docker):
        self.docker = docker

    async def list(self, *, filters: Optional[Dict]=None) -> List[Dict]:
        """
        Return a list of services

        Args:
            filters: a dict with a list of filters

        Available filters:
            id=<service id>
            label=<service label>
            mode=["replicated"|"global"]
            name=<service name>
        """

        params = {"filters": clean_filters(filters)}

        response = await self.docker._query_json(
            "services",
            method="GET",
            params=params
        )
        return response

    async def create(self,
                     task_template: Dict[str, Any],
                     *,
                     name: Optional[str]=None,
                     labels: Optional[List]=None,
                     mode: Optional[Dict]=None,
                     update_config: Optional[Dict]=None,
                     rollback_config: Optional[Dict]=None,
                     networks: Optional[List]=None,
                     endpoint_spec: Optional[Dict]=None
                     ) -> Dict[str, Any]:
        """
        Create a service

        Args:
            task_template: user modifiable task configuration
            name: name of the service
            labels: user-defined key/value metadata
            mode: scheduling mode for the service
            update_config: update strategy of the service
            rollback_config: rollback strategy of the service
            networks: array of network names/IDs to attach the service to
            endpoint_spec: ports to expose

        Returns:
            a dict with info of the created service
        """

        if "Image" not in task_template["ContainerSpec"]:
            raise KeyError(
                "Missing mandatory Image key in ContainerSpec"
            )

        # from {"key":"value"} to ["key=value"]
        if "Env" in task_template["ContainerSpec"]:
            task_template["ContainerSpec"]["Env"] = [
                format_env(k, v)
                for k, v in task_template["ContainerSpec"]["Env"].items()
            ]

        config = {
            "TaskTemplate": task_template,
            "Name": name,
            "Labels": labels,
            "Mode": mode,
            "UpdateConfig": update_config,
            "RollbackConfig": rollback_config,
            "Networks": clean_networks(networks),
            "EndpointSpec": endpoint_spec
        }

        data = json.dumps(clean_config(config))

        response = await self.docker._query_json(
            "services/create",
            method="POST",
            headers={"Content-type": "application/json", },
            data=data,
        )
        return response

    async def delete(self, service_id: str) -> bool:
        """
        Remove a service

        Args:
            service_id: ID or name of the service

        Returns:
            True if successful
        """

        await self.docker._query(
            "services/{service_id}".format(service_id=service_id),
            method="DELETE",
        )
        return True

    async def inspect(self, service_id: str) -> Dict[str, Any]:
        """
        Inspect a service

        Args:
            service_id: ID or name of the service

        Returns:
            a dict with info about a service
        """

        response = await self.docker._query_json(
            "services/{service_id}".format(service_id=service_id),
            method="GET",
        )
        return response