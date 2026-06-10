@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "JAVA_OPTS=-Djava.awt.headless=true"
java %JAVA_OPTS% -jar plantuml.jar activity_diagram.puml
java %JAVA_OPTS% -jar plantuml.jar class_diagram_page1.puml
java %JAVA_OPTS% -jar plantuml.jar class_diagram_page2.puml
java %JAVA_OPTS% -jar plantuml.jar collaboration_diagram.puml
java %JAVA_OPTS% -jar plantuml.jar deployment_diagram_page1.puml
java %JAVA_OPTS% -jar plantuml.jar deployment_diagram_page2.puml
java %JAVA_OPTS% -jar plantuml.jar sequence_diagram_page1.puml
java %JAVA_OPTS% -jar plantuml.jar sequence_diagram_page2.puml
java %JAVA_OPTS% -jar plantuml.jar state_chart_diagram.puml
java %JAVA_OPTS% -jar plantuml.jar usecase_diagram.puml
pause