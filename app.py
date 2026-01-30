import os,sys
import guacamole
import json
from libldap import LibLDAP


if len(sys.argv)==3 and (sys.argv[1]=='-a' or sys.argv[1]=='-d'):
    ldap=LibLDAP()
    filtro={}
    if sys.argv[2] in ['asir1','asir2','smr2','profesores','tituladossmr','tituladosasir','antiguosalumnos']:
        filtro["grupo"]=sys.argv[2]
    else:
        filtro["uid"]=sys.argv[2]
    filtro=ldap.conv_filtro(filtro)
    lista=ldap.buscar(filtro,["sn","uid","givenname"])
    ldap.logout()
    #for usuario in lista:
    #    print(usuario["uid"][0],end=' - ')
    #    print(usuario["givenName"][0]+" "+usuario["sn"][0])

    if len(lista)==0:
        print("No se ha encontrado usuario o grupo")
        sys.exit(1)
    else:
        try:
            session=guacamole.session(os.environ['URL'], "mysql", "guacadmin", os.environ['PASSWORD'])
        except:
            print("No puedo conectar al servidor de guacamole.")
            sys.exit(1)
        if sys.argv[1]=='-d':
            respuesta=input("¿Estás seguro de borrar el usuario/grupo "+sys.argv[2]+" [s/n]?")
            if respuesta=="s":
                for usuario in lista:
                    conn=session.detail_user_permissions(usuario["uid"][0])
                    conn=json.loads(conn)
                    if "connectionPermissions" in conn:
                        for id in conn["connectionPermissions"]:
                            session.delete_connection(id)
                            print("Se ha borrado la conexión",id)
                    session.delete_user(usuario["uid"][0])
                    print("Se ha eliminado el usuario",usuario["givenName"][0]+" "+usuario["sn"][0],"("+usuario["uid"][0]+")")
                    
        else:
            for usuario in lista:
                session.create_user(usuario["uid"][0],"",{"guac-full-name":usuario["givenName"][0]+" "+usuario["sn"][0]})
                session.update_user_permissions(usuario["uid"][0],"add",False,False,True,False,False,False)
                session.update_user_permissions(usuario["uid"][0],"remove",True,True,False,True,True,True)
                print("Se ha añadido el usuario",usuario["givenName"][0]+" "+usuario["sn"][0],"("+usuario["uid"][0]+")")
            
        
    

else:
    print("python3 app.py [-a/-d] [usuario/grupo]")
    print("Indica -a para añadir usuarios o -d para eliminar.")
    print("Debes indicar el id de un usuario o grupo ['asir1','asir2','smr2','profesores','tituladossmr','tituladosasir','antiguosalumnos'].")


