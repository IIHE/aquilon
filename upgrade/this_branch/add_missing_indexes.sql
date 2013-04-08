ALTER TABLE "resource" ADD CONSTRAINT resource_holder_name_type_uk UNIQUE (holder_id, name, resource_type);
ALTER TABLE virtual_machine ADD CONSTRAINT virtual_machine_machine_uk UNIQUE (machine_id);

QUIT;
