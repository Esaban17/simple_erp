#views.py
import json
import sys
import subprocess
from pathlib import Path
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from tienda.models import Pedidos
from tienda.models import Pedidos_Lineas
from tienda.models import Facturas
from tienda.models import Facturas_lineas
from tienda.models import TipoClientes
from tienda.models import Clientes
from tienda.models import Productos
from tienda.models import Paises
from tienda.models import Transportistas
from tienda.models import Monedas
from tienda.models import Incoterms
from tienda.models import Albaranes
from tienda.models import Albaranes_lineas
from .forms import FormularioPaises
from .forms import FormularioTipoClientes
from .forms import FormularioClientes
from .forms import FormularioTransportistas
from .forms import FormularioProductos
from .forms import FormularioPedidos
from .forms import LineasPedidosFormSet
from .forms import FormularioFacturasLineas
from .forms import FormularioCerrarPedidos
from .forms import FormularioCerrarFacturas
from .forms import FormularioEliminarLineasFacturadas
from .forms import FormularioMonedas
from .forms import FormularioFacturas
from .forms import FormularioEliminarLineasPedidos
from .forms import FormularioIncoterms
from .forms import FormularioAlbaranes
from .forms import FormularioCerrarAlbaranes
from .forms import FormularioAlbaranesLineas
from .forms import FormularioEliminarLineasServidas
from .forms import FormularioReabrirPedidos


# Author: Dario Fervenza
# Copyright: Copyright (c) [2023], Dario Fervenza
# Version: 0.1.0
# Maintainer: Dario Fervenza
# Email: dario.fervenza.garcia@gmail.com
# Status: Development

def index(request):
    """ Vista index, contiene un menu
    con las demas paginas
    """
    return render(request,"index.html")
def datos_generales(request):
    """ Vista para introducir y visualizar
    el maestro de paises, transportistas,
    moneda e incoterms
    """
    paises = Paises.objects.all()
    transportistas = Transportistas.objects.all()
    monedas = Monedas.objects.all()
    incoterms = Incoterms.objects.all()
    form_paises = FormularioPaises()
    form_transportistas = FormularioTransportistas()
    form_monedas = FormularioMonedas()
    form_incoterms = FormularioIncoterms()
    if request.method == "POST":
        form_paises = FormularioPaises(request.POST)
        form_transportistas = FormularioTransportistas(request.POST)
        form_monedas = FormularioMonedas(request.POST)
        form_incoterms = FormularioIncoterms(request.POST)
        if form_paises.is_valid():
            form_paises.save()
            return redirect("/datos-generales/")
        if form_transportistas.is_valid():
            form_transportistas.save()
            return redirect("/datos-generales/")
        if form_monedas.is_valid():
            form_monedas.save()
            return redirect("/datos-generales/")
        if form_incoterms.is_valid():
            form_incoterms.save()
            return redirect("/datos-generales/")
    context={
        "form_paises" : form_paises,
        "form_transportistas" : form_transportistas,
        "form_monedas" : form_monedas,
        "form_incoterms" : form_incoterms,
        "transportistas" : transportistas,
        "paises" : paises,
        "monedas" : monedas,
        "incoterms" : incoterms
    }
    return render(request, "datos_generales.html", context)
def entrada_clientes(request):
    """ Vista para introducir y visualizar los clientes y
    los tipos de clientes (1, 2, 3)-> cada tipo, ya sea
    1, 2 o 3 tiene un precio diferente 
    """
    tipo_clientes = TipoClientes.objects.all()
    clientes = Clientes.objects.all()
    form_tipo_clientes = FormularioTipoClientes()
    form_clientes = FormularioClientes()
    if request.method == "POST":
        form_tipo_clientes = FormularioTipoClientes(request.POST)
        form_clientes = FormularioClientes(request.POST)
        if form_tipo_clientes.is_valid():
            form_tipo_clientes.save()
            return redirect("/clientes/")
        if form_clientes.is_valid():
            form_clientes.save()
            return redirect("/clientes/")
    context = {
        "form_tipo_clientes" : form_tipo_clientes,
        "form_clientes" : form_clientes,
        "tipo_clientes" : tipo_clientes,
        "clientes" : clientes,
    }
    return render(request, "clientes.html", context)
def entrada_productos(request):
    """ Vista para introducir y visualizar los productos
    """
    productos = Productos.objects.all()
    form_productos = FormularioProductos()
    if request.method == "POST":
        form_productos = FormularioProductos(request.POST)
        if form_productos.is_valid():
            form_productos.save()
            return redirect("/productos/")
    context = {
        "form_productos" : form_productos,
        "productos" : productos,
        }
    return render(request, "productos.html", context)
def entrada_pedidos(request):
    """ Vista para introducir y visualizar los pedidos
    """
    todos_los_clientes = ""
    if request.method == "GET":
        id_cliente = request.GET.get("id_cliente")
        request.session["id_cliente"]=id_cliente
    id_cliente=request.session.get("id_cliente")
    lista_clientes = list(Clientes.objects.all().values("identificador"))
    lista_clientes = \
        [cliente["identificador"] for cliente in lista_clientes]
    if id_cliente.lower() == "todos" \
    or id_cliente.lower() == "todo" \
    or id_cliente.lower() == "toda" \
    or id_cliente.lower() == "todas" \
    or id_cliente.lower() == "todes" \
    or not id_cliente.isdigit():
        pedidos = Pedidos.objects.all()
        pedidos_lin_data = Pedidos_Lineas.objects.all()
        cliente_name = "todos"
        todos_los_clientes = "yes"
        launch_js_cliente_no_existe = "no"
    else:
        if int(id_cliente) not in lista_clientes:
            launch_js_cliente_no_existe = "si"
            cliente_name = "todos"
            pedidos = Pedidos.objects.all()
            pedidos_lin_data = Pedidos_Lineas.objects.all()
        else:
            cliente = Clientes.objects.filter(identificador=id_cliente)
            launch_js_cliente_no_existe = "no"
            cliente_name = cliente.values("cliente").first()["cliente"]
            pedidos = Pedidos.objects.filter(cliente=cliente_name)
            pedidos_lin_data = \
                Pedidos_Lineas.objects.filter(cliente=cliente_name)
            #return redirect("/facturas/?id_cliente=todos")
    form_pedidos = FormularioPedidos()
    form_lineas_pedidos = \
        LineasPedidosFormSet(form_kwargs={'cliente_name': cliente_name})
    form_cerrar_pedidos = \
        FormularioCerrarPedidos(cliente_name=cliente_name)
    form_eliminar_lineas_pedidos = \
        FormularioEliminarLineasPedidos()
    form_reabrir_pedidos = \
        FormularioReabrirPedidos(cliente_name=cliente_name)
    if request.method == "POST":
        form_pedidos = FormularioPedidos(request.POST)
        form_lineas_pedidos = \
            LineasPedidosFormSet(
                request.POST,
                form_kwargs={'cliente_name': cliente_name}
                )
        form_cerrar_pedidos = \
            FormularioCerrarPedidos(
                request.POST,
                cliente_name=cliente_name
                )
        form_eliminar_lineas_pedidos = \
            FormularioEliminarLineasPedidos(request.POST)
        form_reabrir_pedidos = \
            FormularioReabrirPedidos(
                request.POST,
                cliente_name=cliente_name
                )
        if form_pedidos.is_valid():
            form_pedidos.save()
            return redirect("/pedidos/?id_cliente=" + str(id_cliente))
        if form_lineas_pedidos.is_valid():
            instanciasGuardadas = []
            for form in form_lineas_pedidos.forms:
                if form.cleaned_data.get("num_pedido") \
                and form.cleaned_data.get("codigo_articulo") \
                and form.cleaned_data.get("cantidad"):
                    instanciasGuardadas.append(form.save(commit=False))
            for instancia in instanciasGuardadas:
                instancia.save()
            return redirect("/pedidos/?id_cliente=" + str(id_cliente))
        if form_cerrar_pedidos.is_valid():
            form_cerrar_pedidos.cerrar_pedido()
            return redirect("/pedidos/?id_cliente=" + str(id_cliente))
        if form_reabrir_pedidos.is_valid():
            form_reabrir_pedidos.reabrir_pedido()
            return redirect("/pedidos/?id_cliente=" + str(id_cliente))
        if form_eliminar_lineas_pedidos.is_valid():
            identificador_linea_pedidos = \
                form_eliminar_lineas_pedidos.cleaned_data["identificador"]
            mi_linea_de_pedidos = get_object_or_404(
                Pedidos_Lineas,
                identificador=identificador_linea_pedidos
                )
            cantidad_facturada_eliminar = \
                mi_linea_de_pedidos.cantidad_facturada
            cantidad_servida_eliminar = \
                mi_linea_de_pedidos.cantidad_servida
            if cantidad_facturada_eliminar == 0 \
            and cantidad_servida_eliminar == 0:
                num_pedido_eliminar_ped_lin = mi_linea_de_pedidos.num_pedido_id
                pedido_eliminar_object = \
                    Pedidos.objects.filter(num_pedido=num_pedido_eliminar_ped_lin)
                pedido_abierto_o_cerrado = \
                    pedido_eliminar_object.values("cerrado").first()["cerrado"]
                if not pedido_abierto_o_cerrado:
                    id_cliente_eliminar_pedido_lin = \
                        pedido_eliminar_object\
                        .values("id_cliente")\
                        .first()["id_cliente"]
                    if str(id_cliente).strip() == \
                        str(id_cliente_eliminar_pedido_lin).strip():
                        mi_linea_de_pedidos.delete()
                        # no calcula bien la canitdad de
                        #precio total al elimimnar, tengo que ver eso
                else:
                    pass
            return redirect("/pedidos/?id_cliente=" + str(id_cliente))
    context = {
        "form_pedidos" : form_pedidos,
        "form_lineas_pedidos" : form_lineas_pedidos,
        "form_cerrar_pedidos" : form_cerrar_pedidos,
        "form_eliminar_lineas_pedidos" : form_eliminar_lineas_pedidos,
        "form_reabrir_pedidos" : form_reabrir_pedidos,
        "pedidos" : pedidos,
        "pedidos_lin_data" : pedidos_lin_data,
        "launch_js_cliente_no_existe" : launch_js_cliente_no_existe,
        "todos_los_clientes" : todos_los_clientes,
        "cliente_name" : cliente_name
        }
    return render(request, "pedidos.html", context)
#@login_required
def entrada_facturas(request):
    """ Vista para introducir y visualizar los facturas,
    contiene ademas un boton para generar el excel de
    factura
    """
    todos_los_clientes = ""
    if request.method == "GET":
        id_cliente = request.GET.get("id_cliente")
        request.session["id_cliente"] = id_cliente
        # no es necesario usar variable
        #de sesion pero queda como ejemplo de uso
    id_cliente = request.session.get("id_cliente")
    lista_clientes = \
        list(Clientes.objects.all().values("identificador"))
    lista_clientes = \
        [cliente["identificador"] for cliente in lista_clientes]
    if id_cliente.lower() == "todos" \
    or id_cliente.lower() == "todo" \
    or id_cliente.lower() == "toda" \
    or id_cliente.lower() == "todas" \
    or id_cliente.lower() == "todes" \
    or not id_cliente.isdigit():
        facturas = Facturas.objects.all()
        order_choices = Pedidos_Lineas.objects.filter(cerrado=False)
        form_facturas_lineas = FormularioFacturasLineas(order_choices,"todos")
        todos_los_clientes = "yes"
        facturas_lineas = Facturas_lineas.objects.all()
        cliente_name = "todos"
        launch_js_cliente_no_existe = "no"
    else:
        if int(id_cliente) not in lista_clientes:
            launch_js_cliente_no_existe = "si"
            cliente_name = "todos"
            cliente = Clientes.objects.all()
            facturas = Facturas.objects.all()
            facturas_lineas = Facturas_lineas.objects.all()
            order_choices = Pedidos_Lineas.objects.filter(cerrado=False)
        else:
            launch_js_cliente_no_existe = "no"
            cliente = Clientes.objects.filter(identificador=id_cliente)
            cliente_name = cliente.values("cliente").first()["cliente"]
            facturas = Facturas.objects.filter(cliente=cliente_name)
            order_choices = \
                Pedidos_Lineas\
                .objects\
                .filter(cliente=cliente_name)\
                .filter(cerrado=False)
            facturas_lineas = \
                Facturas_lineas.objects.filter(cliente=cliente_name)
        form_facturas_lineas = \
            FormularioFacturasLineas(order_choices,cliente_name)
    #cliente = \
        #Clientes.objects.filter(identificador=id_cliente)\
        #.values("cliente")[0]
    form_facturas = FormularioFacturas()
    form_cerrar_facturas = \
        FormularioCerrarFacturas(cliente_name=cliente_name)
    form_eliminar_lineas = \
        FormularioEliminarLineasFacturadas()
    if request.method == "POST":
        form_facturas = FormularioFacturas(request.POST)
        form_cerrar_facturas = \
            FormularioCerrarFacturas(
                request.POST,
                cliente_name=cliente_name
                )
        form_facturas_lineas = \
            FormularioFacturasLineas(
                order_choices,
                cliente_name,
                request.POST
                )
        form_eliminar_lineas = \
            FormularioEliminarLineasFacturadas(request.POST)
        if form_facturas.is_valid():
            cliente = form_facturas.cleaned_data["cliente"]
            id_cliente = \
                Clientes\
                .objects\
                .filter(cliente=cliente)\
                .values("identificador")\
                .first()["identificador"]
            form_facturas.save()
            return redirect("/facturas/?id_cliente=" + str(id_cliente))
        if form_cerrar_facturas.is_valid():
            form_cerrar_facturas.cerrar_factura()
            return redirect("/facturas/?id_cliente=" + str(id_cliente))
        if form_facturas_lineas.is_valid():
            for order in order_choices:
                identificador_ped = order.identificador
                num_pedido = order.num_pedido
                codigo_articulo = order.codigo_articulo
                cantidad_restante = order.cantidad - order.cantidad_facturada
                if cantidad_restante > 0:
                    cantidad_servida = \
                        form_facturas_lineas\
                        .cleaned_data[f"Facturado_{identificador_ped}"]
                    if cantidad_servida > 0:
                        elemento_facturado = Facturas_lineas(
                            num_factura=form_facturas_lineas\
                                       .cleaned_data["num_factura"],
                            identificador_linea_pedido=identificador_ped,
                            num_pedido=num_pedido,
                            codigo_articulo=codigo_articulo,
                            cantidad_total=order.cantidad,
                            cantidad_facturada=cantidad_servida,
                            )
                        elemento_facturado.save()
            return redirect("/facturas/?id_cliente=" + str(id_cliente))
        if form_eliminar_lineas.is_valid():
            #añadir funcion para eliminar lineas de pedidos
            #solo si la cantidad facturada es cero y la antidad servida
            #añadir funciones de albaran
            identificador_linea_facturas = \
                form_eliminar_lineas.cleaned_data["identificador"]
            mi_linea_de_facturas = get_object_or_404(
                Facturas_lineas,
                identificador=identificador_linea_facturas
                )
            num_factura_eliminar_fact_lin = \
                mi_linea_de_facturas.num_factura_id
            factura_eliminar_object = Facturas.objects.filter(
                num_factura=num_factura_eliminar_fact_lin
                )
            factura_abierta_o_cerrada = factura_eliminar_object\
                                        .values("cerrado")\
                                        .first()["cerrado"]
            if not factura_abierta_o_cerrada:
                id_cliente_eliminar_fact_lin = factura_eliminar_object\
                                               .values("id_cliente")\
                                               .first()["id_cliente"]
                id_cliente_strip = str(id_cliente).strip()
                id_fact_strp = str(id_cliente_eliminar_fact_lin).strip()
                if id_cliente_strip == id_fact_strp:
                    mi_linea_de_facturas.delete()
            else:
                pass
            return redirect("/facturas/?id_cliente=" + str(id_cliente))
    context = {
        "form_facturas" : form_facturas,
        "form_cerrar_facturas" : form_cerrar_facturas,
        "form_facturas_lineas" : form_facturas_lineas,
        "facturas" : facturas,
        "facturas_lineas" : facturas_lineas,
        "todos_los_clientes" : todos_los_clientes,
        "form_eliminar_lineas" : form_eliminar_lineas,
        "launch_js_cliente_no_existe" : launch_js_cliente_no_existe,
        "cliente_name" : cliente_name
    }
    return render (request, "facturar.html", context)
def entrada_albaranes(request):
    """ Vista para introducir y visualizar los albaranes,
    contiene un form para generar el excel de un
    albaran
    """
    todos_los_clientes = ""
    if request.method == "GET":
        id_cliente = request.GET.get("id_cliente")
        request.session["id_cliente"] = id_cliente
    id_cliente = request.session.get("id_cliente")
    lista_clientes = \
        list(Clientes.objects.all().values("identificador"))
    lista_clientes = \
        [cliente["identificador"] for cliente in lista_clientes]
    if id_cliente.lower() == "todos" \
    or id_cliente.lower() == "todo" \
    or id_cliente.lower() == "toda" \
    or id_cliente.lower() == "todas" \
    or id_cliente.lower() == "todes" \
    or not id_cliente.isdigit():
        albaranes = Albaranes.objects.all()
        order_choices = Pedidos_Lineas.objects.filter(cerrado=False)
        form_albaranes_lineas = \
            FormularioAlbaranesLineas(order_choices,"todos")
        todos_los_clientes = "yes"
        albaranes_lineas = Albaranes_lineas.objects.all()
        cliente_name = "todos"
        launch_js_cliente_no_existe = "no"
    else:
        if int(id_cliente) not in lista_clientes:
            launch_js_cliente_no_existe = "si"
            cliente_name = "todos"
            cliente = Clientes.objects.all()
            albaranes = Albaranes.objects.all()
            albaranes_lineas = Albaranes_lineas.objects.all()
            order_choices = Pedidos_Lineas.objects.filter(cerrado=False)
        else:
            launch_js_cliente_no_existe = "no"
            cliente = Clientes.objects.filter(identificador=id_cliente)
            cliente_name = cliente.values("cliente").first()["cliente"]
            albaranes = Albaranes.objects.filter(cliente=cliente_name)
            order_choices = \
                Pedidos_Lineas\
                .objects\
                .filter(cliente=cliente_name)\
                .filter(cerrado=False)
            albaranes_lineas = \
                Albaranes_lineas.objects.filter(cliente=cliente_name)
        form_albaranes_lineas = \
            FormularioAlbaranesLineas(order_choices,cliente_name)
    form_albaranes = FormularioAlbaranes()
    form_cerrar_albaranes = \
        FormularioCerrarAlbaranes(cliente_name=cliente_name)
    form_eliminar_lineas_albaranes = \
        FormularioEliminarLineasServidas()
    if request.method == "POST":
        form_albaranes = FormularioAlbaranes(request.POST)
        form_cerrar_albaranes = \
            FormularioCerrarAlbaranes(
                request.POST,
                cliente_name=cliente_name
                )
        form_albaranes_lineas = FormularioAlbaranesLineas(
            order_choices,
            cliente_name,
            request.POST
            )
        form_eliminar_lineas_albaranes = \
            FormularioEliminarLineasServidas(request.POST)
        if form_albaranes.is_valid():
            cliente = form_albaranes.cleaned_data["cliente"]
            id_cliente = \
                Clientes\
                .objects\
                .filter(cliente=cliente)\
                .values("identificador")\
                .first()["identificador"]
            form_albaranes.save()
            return redirect("/albaranes/?id_cliente=" + str(id_cliente))
        if form_cerrar_albaranes.is_valid():
            form_cerrar_albaranes.cerrar_albaran()
            return redirect("/albaranes/?id_cliente=" + str(id_cliente))
        if form_albaranes_lineas.is_valid():
            for order in order_choices:
                identificador_ped = order.identificador
                num_pedido = order.num_pedido
                codigo_articulo = order.codigo_articulo
                cantidad_restante = order.cantidad - order.cantidad_servida
                if cantidad_restante > 0:
                    cantidad_servida = \
                        form_albaranes_lineas\
                        .cleaned_data[f"Servido_{identificador_ped}"]
                    if cantidad_servida > 0:
                        elemento_servido = Albaranes_lineas(
                            num_albaran=form_albaranes_lineas.cleaned_data["num_albaran"],
                            identificador_linea_pedido=identificador_ped,
                            num_pedido=num_pedido,
                            codigo_articulo=codigo_articulo,
                            cantidad_total=order.cantidad,
                            cantidad_servida=cantidad_servida,
                            )
                        elemento_servido.save()
            return redirect("/albaranes/?id_cliente=" + str(id_cliente))
        if form_eliminar_lineas_albaranes.is_valid():
            identificador_linea_albaranes = \
                form_eliminar_lineas_albaranes\
                .cleaned_data["identificador"]
            mi_linea_de_albaranes = get_object_or_404(
                Albaranes_lineas,
                identificador=identificador_linea_albaranes
                )
            num_albaran_eliminar_alb_lin = \
                mi_linea_de_albaranes.num_albaran_id
            albaran_eliminar_object = \
                Albaranes.objects.filter(num_albaran=num_albaran_eliminar_alb_lin)
            albaran_abierta_o_cerrada = \
                albaran_eliminar_object.values("cerrado").first()["cerrado"]
            if not albaran_abierta_o_cerrada:
                id_cliente_eliminar_alb_lin = \
                    albaran_eliminar_object\
                    .values("id_cliente")\
                    .first()["id_cliente"]
                print(id_cliente_eliminar_alb_lin)
                id_cli_strp = str(id_cliente).strip()
                id_elim_strp = str(id_cliente_eliminar_alb_lin).strip()
                if id_cli_strp == id_elim_strp:
                    mi_linea_de_albaranes.delete()
            else:
                pass
            return redirect("/albaranes/?id_cliente=" + str(id_cliente))
    context = {
        "form_albaranes" : form_albaranes,
        "form_cerrar_albaranes" : form_cerrar_albaranes,
        "form_albaranes_lineas" : form_albaranes_lineas,
        "albaranes" : albaranes,
        "albaranes_lineas" : albaranes_lineas,
        "todos_los_clientes" : todos_los_clientes,
        "form_eliminar_lineas_albaranes" : form_eliminar_lineas_albaranes,
        "launch_js_cliente_no_existe" : launch_js_cliente_no_existe,
        "cliente_name" : cliente_name
        }
    return render (request,"servir.html", context)
def lanzar_factura(request):
    """ vista que genera el excel de la factura,
    es llamada por la vista de facturas
    """
    num_factura = request.POST.get("num_factura")
    datos_json = json.loads(serializers.serialize(
        'json',
        Facturas.objects.filter(num_factura=num_factura)
        ))
    datos = json.dumps(datos_json)
    productos_json = json.loads(serializers.serialize(
        "json",
        Productos.objects.all()
        ))
    productos = json.dumps(productos_json)
    facturas_lineas_json = json.loads(serializers.serialize(
        "json",
        Facturas_lineas.objects.filter(num_factura=num_factura)
        ))
    facturas_lineas = json.dumps(facturas_lineas_json)
    # sys.executable usa el mismo intérprete que corre Django — resuelve PAIN_LOG #16
    # Path(__file__).parent apunta al directorio gestor/ — resuelve PAIN_LOG #10
    script_path = str(Path(__file__).parent / "lanzar_factura.py")
    subprocess.check_call([
        sys.executable,
        script_path,
        datos,
        productos,
        facturas_lineas,
        "factura"
        ])
    return HttpResponse("Factura lanzada")
def lanzar_albaran(request):
    """ vista que genera el excel del albaran,
    es llamada por la vista de facturas
    """
    num_albaran = request.POST.get("num_albaran")
    datos_json = json.loads(serializers.serialize(
        'json',
        Albaranes.objects.filter(num_albaran=num_albaran)
        ))
    datos = json.dumps(datos_json)
    productos_json = json.loads(serializers.serialize(
        "json",
        Productos.objects.all()
        ))
    productos = json.dumps(productos_json)
    albaranes_lineas_json = json.loads(serializers.serialize(
        "json",
        Albaranes_lineas.objects.filter(num_albaran=num_albaran)
        ))
    albaranes_lineas = json.dumps(albaranes_lineas_json)
    try:
        script_path = str(Path(__file__).parent / "lanzar_albaran.py")
        salida = subprocess.check_call([
            sys.executable,
            script_path,
            datos,
            productos,
            albaranes_lineas,
            "albaran"
            ])
        response = "ok"
    except Exception as e:
        error = e
        response = error
    return HttpResponse(response)
