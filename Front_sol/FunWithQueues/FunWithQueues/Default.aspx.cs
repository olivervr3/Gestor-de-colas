using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Net;
using System.Threading;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;

namespace FunWithQueues
{
    public partial class _Default : Page
    {

        private int getCuadrante(int x, int y) {
            if (x >= 0 && x <= 9)
            {
                if (y >= 0 && y <= 9)
                {
                    return 1;
                }
                else
                {
                    return 3;
                }
            }
            else
            {
                if (y >= 0 && y <= 9)
                {
                    return 2;
                }
                else
                {
                    return 4;
                }
            }
        }

        private void setTemp(int t0,int t1, int t2, int t3)
        {

            if (t0 == -1)
            {
                Label14.ForeColor = System.Drawing.Color.Black;
                Label14.BackColor = System.Drawing.Color.Yellow;
                Label14.Text = "CUADRANTE ARRIBA IZQUIERDA: ¡¡No se conoce el tiempo!!";
            }
            else if (t0 < 20 || t0 > 30)
            {
                Label14.ForeColor = System.Drawing.Color.Red;
                Label14.Text = "CUADRANTE ARRIBA IZQUIERDA: ¡¡Zona Cerrada!! La temperatura no es apta -> " + t0.ToString() + "ºC";
            }
            else
            {
                Label14.ForeColor = System.Drawing.Color.DarkGreen;
                Label14.Text = "CUADRANTE ARRIBA IZQUIERDA: Zona abierta, clima estable, pasatelo bien :) -> " + t0.ToString() + "ºC";
            }


            if (t1 == -1)
            {
                Label15.ForeColor = System.Drawing.Color.DarkGoldenrod;
                Label15.Text = "CUADRANTE ARRIBA DERECHA: ¡¡No se conoce el tiempo!!";
            }
            else if (t1 < 20 || t1 > 30)
            {
                Label15.ForeColor = System.Drawing.Color.Red;
                Label15.Text = "CUADRANTE ARRIBA DERECHA: ¡¡Zona Cerrada!! La temperatura no es apta -> " + t1.ToString() + "ºC";
            }
            else
            {
                Label15.ForeColor = System.Drawing.Color.DarkGreen;
                Label15.Text = "CUADRANTE ARRIBA DERECHA: Zona abierta, clima estable, pasatelo bien :) -> " + t1.ToString() + "ºC";
            }


            if (t2 == -1)
            {
                Label16.ForeColor = System.Drawing.Color.DarkGoldenrod;
                Label16.Text = "CUADRANTE ABAJO IZQUIERDA: ¡¡No se conoce el tiempo!!";
            }
            else if (t2 < 20 || t2 > 30)
            {
                Label16.ForeColor = System.Drawing.Color.Red;
                Label16.Text = "CUADRANTE ABAJO IZQUIERDA: ¡¡Zona Cerrada!! La temperatura no es apta -> " + t2.ToString() + "ºC";
            }
            else
            {
                Label16.ForeColor = System.Drawing.Color.DarkGreen;
                Label16.Text = "CUADRANTE ABAJO IZQUIERDA: Zona abierta, clima estable, pasatelo bien :) -> " + t2.ToString() + "ºC";
            }

            if (t3 == -1)
            {
                Label17.ForeColor = System.Drawing.Color.DarkGoldenrod;
                Label17.Text = "CUADRANTE ABAJO DERECHA: ¡¡No se conoce el tiempo!!";
            }
            else if (t3 < 20 || t3 > 30)
            {
                Label17.ForeColor = System.Drawing.Color.Red;
                Label17.Text = "CUADRANTE ABAJO DERECHA: ¡¡Zona Cerrada!! La temperatura no es apta -> " + t3.ToString() + "ºC";
            }
            else
            {
                Label17.ForeColor = System.Drawing.Color.DarkGreen;
                Label17.Text = "CUADRANTE ABAJO DERECHA: Zona abierta, clima estable, pasatelo bien :) -> " + t3.ToString() + "ºC";
            }
        }

        private void loadMap()
        {
            string html = string.Empty;
            string url = @"https://localhost:8080/map";

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);

            request.AutomaticDecompression = DecompressionMethods.GZip;
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };
            using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
            using (Stream stream = response.GetResponseStream())
            using (StreamReader reader = new StreamReader(stream))
            {
                html = reader.ReadToEnd();
            }
            var details = JObject.Parse(html);

            if (details["online"].ToString() == "0")
            {
                Label1.Text = "No se tiene informacion reciente del parque puede que esté cerrado";
                Label1.ForeColor = System.Drawing.Color.Red;
            }
            else
            {

                int t0 = Int32.Parse(details["cities"][0]["temp"].ToString());
                int t1 = Int32.Parse(details["cities"][1]["temp"].ToString());
                int t2 = Int32.Parse(details["cities"][2]["temp"].ToString());
                int t3 = Int32.Parse(details["cities"][3]["temp"].ToString());

                setTemp(t0, t1, t2, t3); 

                String[,] mapa = new string[20, 20];

                for (int i = 0; i < 20; i++)
                {
                    for (int j = 0; j < 20; j++)
                    {
                        int cuadrante = getCuadrante(i, j);
                        int temp;
                        if (cuadrante == 1)
                        {
                            temp = t0;
                        }
                        else if (cuadrante == 2)
                        {
                            temp = t1;
                        }
                        else if (cuadrante == 3)
                        {
                            temp = t2;
                        }
                        else
                        {
                            temp = t3;
                        }

                        if (temp == -1)
                        {
                            mapa[i, j] = "#";
                        }
                        else if (temp < 20 || temp > 30)
                        {
                            mapa[i, j] = "X";
                        }
                        else
                        {
                            mapa[i, j] = "-";
                        }



                    }
                }

                int x, y, et;
                int id;
                for (int i = 0; i < details["attractions"].Count(); i++)
                {
                    id = Int32.Parse(details["attractions"][i]["id"].ToString());
                    x = Int32.Parse(details["attractions"][i]["X"].ToString());
                    y = Int32.Parse(details["attractions"][i]["Y"].ToString());
                    et = Int32.Parse(details["attractions"][i]["et"].ToString());

                    if (et == -1)
                    {
                        // No se conoce el tiempo
                        mapa[x, y] = "[" + id + "/?]";
                    }
                    else
                    {
                        mapa[x, y] = "[" + id + "/" + et.ToString() + "]";
                    }
                }

                String nombre;
                int atDirige;
                String us = ""; 

                for (int i = 0; i < details["users"].Count(); i++)
                {
                    x = Int32.Parse(details["users"][i]["X"].ToString());
                    y = Int32.Parse(details["users"][i]["Y"].ToString());
                    nombre = details["users"][i]["nombre"].ToString();
                    atDirige = Int32.Parse(details["users"][i]["at"].ToString());

                    if (nombre.Length != 1 && nombre.Length != 2)
                    {
                        nombre = nombre.Substring(0, 2);
                    }
                    if (x >= 0 && x <= 19 && y >= 0 && y <= 19)
                    {
                        mapa[x, y] = mapa[x, y] + " [" + nombre + "]";

                        us = us + "El usuario [" + nombre + "] ";
                        us = us + "esta en la posicion [X, Y] = [" + (x+1).ToString() + ", " + (y+1).ToString() + "]";
                        if (atDirige != 0)
                        {
                            x = Int32.Parse(details["attractions"][(atDirige-1)]["X"].ToString()) +1;
                            y = Int32.Parse(details["attractions"][(atDirige-1)]["Y"].ToString()) + 1;
                            us = us + " y se dirige a la atraccion " + atDirige.ToString() + "-> [" + x.ToString() + ", " + y.ToString() + "]";
                        }
                        else
                        {
                            us = us + " y no se dirige a ninguna atraccion";
                        }
                        us = us + "<br/>"; 
                    }
                }

                if (details["users"].Count() == 0)
                {
                    Label12.Text = "No hay usuarios dentro del parque en este momento"; 
                }
                else
                {
                    Label12.Text = us;

                }

                DataTable table = new DataTable();
                table.Columns.Add("-");
                for (int i = 0; i < 20; i++)
                {
                    table.Columns.Add((i+1).ToString());
                }

                for (int i = 0; i < 20; i++)
                {
                    DataRow row = table.NewRow();
                    row["-"] = (i+1).ToString(); 
                    for (int j = 0; j < 20; j++)
                    {
                        row[(j+1).ToString()] = "    " + mapa[j, i] + "     ";
                    }
                    table.Rows.Add(row);
                }

                DataRow row2 = table.NewRow();
                for (int j = 0; j < 20; j++)
                {
                    row2[(j+1).ToString()] = "------------------";
                }

                table.Rows.Add(row2);

                GridView1.DataSource = table;
                GridView1.DataBind();



            }
        } 

        protected void Page_Load(object sender, EventArgs e)
        {
            try
            {
                loadMap();

            }
            catch
            {
                Label1.Text = "No se ha podido conectar al servidor API";
                Label1.ForeColor = System.Drawing.Color.Red; 
            }
        }

        protected void Button1_Click(object sender, EventArgs e)
        {
            Response.Redirect("~/Default.aspx"); 
        
        }

    }
}