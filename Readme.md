# Entrega Proyecto 2
## Guía para desplegar 
1. **Clonar el repositorio en la carpeta desde la que se quiere ejecutar el notebook**
   ```console
   git clone https://github.com/danielj4mv/proyecto_2.git
   ```
2. **Ingresar desde la terminal a la carpeta en que se encuentra el archivo `docker-compose.yml`**
   ```docker
   cd proyecto_2
   ```
3. **Crear la siguiente variable de entorno para poder modificar volúmenes**
   ```console
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   ```
4. **Crear y ejecutar los servicios establecidos en el `docker-compose.yml`**

   ```docker
   docker compose up
   ```
   Este proceso puede tomar varios minutos, espere a que termine de ejecutar para pasar al siguiente paso

5. **Una vez se ha terminado de ejecutar el comando anterior, puede proceder a interactuar con los servicios a través de sus apis:**

   - **Airflow:** puerto 8080, las credenciales de acceso están definidas en el `.env`
   - **MLflow:** puerto 5000
   - **Minio:** puerto 9000, las credenciales de acceso están definidas en el `.env`

   Recuerde que si el ingreso es dessde la máquina virtual debe ir a `IP_de_la_MV:Puerto`, desde el pc local sería `Localhost:Puerto`

