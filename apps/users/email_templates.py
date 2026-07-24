def get_codeacademy_html_email(title, content_html, call_to_action=None):
    """
    Genera un correo HTML con temática Dark Mode / Neon para CodeAcademy.
    """
    
    cta_html = ""
    if call_to_action:
        url = call_to_action.get('url', '#')
        text = call_to_action.get('text', 'Haz clic aquí')
        cta_html = f"""
        <div style="text-align: center; margin-top: 30px;">
            <a href="{url}" style="background: linear-gradient(90deg, #00f260 0%, #0575e6 100%); color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px; box-shadow: 0 4px 15px rgba(0, 242, 96, 0.4);">
                {text}
            </a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e2e8f0; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; overflow: hidden; margin-top: 40px; margin-bottom: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px 20px; text-align: center; border-bottom: 2px solid #00f260;">
                <h1 style="margin: 0; color: #ffffff; font-size: 28px; letter-spacing: 1px;">
                    <span style="color: #00f260;">&lt;</span>Code<span style="color: #00f260;">Academy/&gt;</span>
                </h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #ffffff; margin-top: 0; font-size: 22px;">{title}</h2>
                <div style="color: #cbd5e1; font-size: 16px;">
                    {content_html}
                </div>
                
                {cta_html}
                
                <hr style="border: 0; border-top: 1px solid #334155; margin: 40px 0 20px 0;">
                <p style="font-size: 13px; color: #64748b; margin: 0; text-align: center;">
                    Este correo fue generado automáticamente por la plataforma CodeAcademy. No respondas a esta dirección.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
