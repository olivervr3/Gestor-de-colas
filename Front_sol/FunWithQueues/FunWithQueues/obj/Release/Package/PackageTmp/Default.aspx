<%@ Page Title="FunWithQueues" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="FunWithQueues._Default" Async="true" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <style>
        .don{
            text-align: center; 
        }
    </style>
    <br />
    <br />
    <asp:Label ID="Label1" runat="server" Text="" Font-Size="24px"></asp:Label><br />

    <asp:Label ID="Label2" runat="server" Text="Leyenda del mapa" Font-Size="20px"></asp:Label><br />
    <asp:Label ID="Label6" runat="server" Text="Estado del parque" Font-Size="16px" Font-Bold="true" Font-Underline="true"></asp:Label><br>

    <asp:Label ID="Label3" runat="server" Text="[ # ] = No se conoce información sobre la temperatura en esta zona"></asp:Label> <br />
    <asp:Label ID="Label4" runat="server" Text="[ X ] = La zona del parque está cerrada"></asp:Label>  <br />
    <asp:Label ID="Label5" runat="server" Text="[ - ] = La zona del parque se encuentra activa"></asp:Label>  <br /><br />

        <asp:Label ID="Label7" runat="server" Text="Visitantes" Font-Size="16px" Font-Bold="true" Font-Underline="true"></asp:Label><br />
     <asp:Label ID="Label8" runat="server" Text="[ nombre ] = Los visitantes que se encuentren en el mapa tendrán un pseudonombre, sus 2 caracteres de su usuario, en la posición donde se encuentren"></asp:Label> <br />
    <br />

    <asp:Label ID="Label9" runat="server" Text="Atracciones" Font-Size="16px" Font-Bold="true" Font-Underline="true"></asp:Label><br />
     <asp:Label ID="Label10" runat="server" Text="[ id/Tiempo ] = Si no se conoce el tiempo de una atraccion se mostrará ? [id/?]"></asp:Label> <br />

    
    <div></div>
    <center>
        </center>
    <br />
    <br />
    <br />

        <asp:GridView ID="GridView1" runat="server" RowStyle-Width="75px" RowStyle-Height="35px" HorizontalAlign="Center">
            <RowStyle Height="35px" Width="75px" CssClass="don"></RowStyle>
        </asp:GridView>

    <br />
    <br />
    <asp:Label ID="Label11" runat="server" Text="Visitantes" Font-Size="16px" Font-Bold="true" Font-Underline="true"></asp:Label><br />
    <asp:Label ID="Label12" runat="server" Text="Visitantes" ></asp:Label><br />
       <asp:Label ID="Label13" runat="server" Text="Temperatura" Font-Size="16px" Font-Bold="true" Font-Underline="true"></asp:Label><br />
    <asp:Label ID="Label14" runat="server" Text="" ></asp:Label><br />
    <asp:Label ID="Label15" runat="server" Text="" ></asp:Label><br />
    <asp:Label ID="Label16" runat="server" Text="" ></asp:Label><br />
    <asp:Label ID="Label17" runat="server" Text="" ></asp:Label><br />


</asp:Content>
