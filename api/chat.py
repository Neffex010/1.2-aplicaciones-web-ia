import json
import os

from http.server import BaseHTTPRequestHandler
from openai import OpenAI


ALLOWED_ORIGIN = os.environ.get(
   "ALLOWED_ORIGIN",
   ""
).rstrip("/")


class handler(BaseHTTPRequestHandler):

   def add_cors_headers(self):
       origin = self.headers.get("Origin", "")

       if ALLOWED_ORIGIN and origin == ALLOWED_ORIGIN:
           self.send_header(
               "Access-Control-Allow-Origin",
               origin
           )
           self.send_header("Vary", "Origin")


   def send_json(self, status_code, data):
       body = json.dumps(
           data,
           ensure_ascii=False
       ).encode("utf-8")

       self.send_response(status_code)
       self.send_header(
           "Content-Type",
           "application/json; charset=utf-8"
       )
       self.add_cors_headers()
       self.send_header(
           "Content-Length",
           str(len(body))
       )
       self.end_headers()

       self.wfile.write(body)


   def do_OPTIONS(self):
       origin = self.headers.get("Origin", "")

       if ALLOWED_ORIGIN and origin != ALLOWED_ORIGIN:
           self.send_response(403)
           self.end_headers()
           return

       self.send_response(204)
       self.add_cors_headers()
       self.send_header(
           "Access-Control-Allow-Methods",
           "POST, OPTIONS"
       )
       self.send_header(
           "Access-Control-Allow-Headers",
           "Content-Type"
       )
       self.send_header(
           "Access-Control-Max-Age",
           "86400"
       )
       self.end_headers()


   def do_GET(self):
       self.send_json(
           405,
           {
               "error":
                   "Este endpoint solamente acepta POST."
           }
       )


   def do_POST(self):
       try:
           origin = self.headers.get("Origin", "")

           if ALLOWED_ORIGIN and origin != ALLOWED_ORIGIN:
               self.send_json(
                   403,
                   {"error": "Origen no autorizado."}
               )
               return

           content_length = int(
               self.headers.get("Content-Length", 0)
           )

           if content_length <= 0 or content_length > 5000:
               self.send_json(
                   413,
                   {"error": "Petición no válida o demasiado grande."}
               )
               return

           body = self.rfile.read(content_length)

           data = json.loads(
               body.decode("utf-8")
           )

           message = str(
               data.get("message", "")
           ).strip()

           if not message:
               self.send_json(
                   400,
                   {"error": "Es necesario escribir un mensaje."}
               )
               return

           if len(message) > 1000:
               self.send_json(
                   400,
                   {"error": "El mensaje supera los 1000 caracteres."}
               )
               return

           api_key = os.environ.get(
               "OPENAI_API_KEY"
           )

           if not api_key:
               self.send_json(
                   500,
                   {"error": "OPENAI_API_KEY no está configurada."}
               )
               return

           client = OpenAI(
               api_key=api_key
           )

           response = client.responses.create(
               model="gpt-5.6-luna",
               instructions="""
               Eres un asistente educativo especializado
               en Tecnologías de Información y Comunicaciones.
               Responde siempre en español, de manera clara,
               breve y didáctica. Incluye ejemplos cuando ayuden
               a comprender el concepto.
               """,
               input=message,
               reasoning={
                   "effort": "none"
               },
               max_output_tokens=500
           )

           self.send_json(
               200,
               {
                   "reply":
                       response.output_text
               }
           )

       except json.JSONDecodeError:
           self.send_json(
               400,
               {"error": "El cuerpo no contiene JSON válido."}
           )

       except Exception as error:
           print(
               f"Error en /api/chat: "
               f"{type(error).__name__}: {error}"
           )

           self.send_json(
               500,
               {
                   "error":
                       "No fue posible consultar el modelo de IA."
               }
           )