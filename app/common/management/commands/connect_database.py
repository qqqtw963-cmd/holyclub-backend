from uuid import uuid4
from xml.etree import ElementTree

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "파이참 데이터베이스를 연결합니다."

    def add_arguments(self, parser):
        parser.add_argument("--host", default=str(settings.DATABASES["default"]["HOST"]), type=str, help="호스트")
        parser.add_argument("--port", "-p", default=str(settings.DATABASES["default"]["PORT"]), type=str, help="포트")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        host = options.get("host")
        port = options.get("port")
        if host:
            database["HOST"] = host
        if port:
            database["PORT"] = port

        uuid = str(uuid4())
        dir_path = settings.BASE_DIR.parent / ".idea"

        self.create_xml_data(dir_path / "dataSources.xml", database, uuid)
        self.create_local_xml_data(dir_path / "dataSources.local.xml", database, uuid)

    def create_xml_data(self, file_path, database, uuid):
        tree, created = self.get_or_create_xml(file_path)
        project = tree.getroot()
        if created:
            component = ElementTree.SubElement(
                project,
                "component",
                name="DataSourceManagerImpl",
                format="xml",
                multifile_model="true",
            )
        else:
            component = project.find(".//component")

        data_source = ElementTree.SubElement(
            component,
            "data-source",
            source="LOCAL",
            name=f"{settings.APP_ENV}",
            uuid=uuid,
        )

        driver_ref = ElementTree.SubElement(data_source, "driver-ref")
        driver_ref.text = "postgresql"

        synchronize = ElementTree.SubElement(data_source, "synchronize")
        synchronize.text = "true"

        jdbc_driver = ElementTree.SubElement(data_source, "jdbc-driver")
        jdbc_driver.text = "org.postgresql.Driver"

        jdbc_url = ElementTree.SubElement(data_source, "jdbc-url")
        jdbc_url.text = f"jdbc:postgresql://{database['HOST']}:{database['PORT']}/{database['NAME']}?password={database['PASSWORD']}"

        working_dir = ElementTree.SubElement(data_source, "working-dir")
        working_dir.text = "$ProjectFileDir$"

        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def create_local_xml_data(self, file_path, database, uuid):
        tree, created = self.get_or_create_xml(file_path)
        project = tree.getroot()
        if created:
            component = ElementTree.SubElement(project, "component", name="dataSourceStorageLocal", created_in="")
        else:
            component = project.find(".//component")

        data_source = ElementTree.SubElement(
            component,
            "data-source",
            name=f"{settings.APP_ENV}",
            uuid=uuid,
        )

        ElementTree.SubElement(
            data_source,
            "database-info",
            product="",
            version="",
            jdbc_version="",
            driver_name="",
            driver_version="",
            dbms="POSTGRES",
        )

        secret_storage = ElementTree.SubElement(data_source, "secret-storage")
        secret_storage.text = "master_key"

        user_name = ElementTree.SubElement(data_source, "user-name")
        user_name.text = database["USER"]

        ElementTree.SubElement(data_source, "schema-mapping")

        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def get_or_create_xml(file_path):
        try:
            tree = ElementTree.parse(file_path)
            created = False
        except FileNotFoundError:
            project = ElementTree.Element("project", version="4")
            tree = ElementTree.ElementTree(project)
            created = True
        return tree, created
