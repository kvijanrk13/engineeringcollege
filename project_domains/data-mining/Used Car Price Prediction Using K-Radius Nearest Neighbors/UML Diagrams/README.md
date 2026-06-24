# UML Diagram Sources

The `.puml` files in this folder can be rendered with PlantUML.

Suggested render command:

```powershell
java -jar plantuml.jar *.puml
```

Included diagrams:

- Use case diagram
- Class diagram
- Activity diagram
- Sequence diagram
- Component diagram
- ER diagram
- Deployment diagram
- Automatic ER diagram generated with `python manage.py graph_models -a -o erd.png`
- Reverse-engineered class and package diagrams generated with `pyreverse -o png car_price_app`
