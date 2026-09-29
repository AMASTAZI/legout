import io
import os
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def generate_invoice_pdf(order):
    """
    Génère un reçu / facture au format PDF haute fidélité pour une commande.
    Utilise la charte graphique chaleureuse (Terracotta #A83B19, Ocre #C27A23, Bois sombre #221C18).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Couleurs de la charte
    COLOR_TERRACOTTA = colors.HexColor('#A83B19')
    COLOR_OCHRE = colors.HexColor('#C27A23')
    COLOR_DARK = colors.HexColor('#221C18')
    COLOR_LIGHT = colors.HexColor('#FAF6F0')
    COLOR_GRAY = colors.HexColor('#6B7280')
    COLOR_RED = colors.HexColor('#DC2626')
    COLOR_GREEN = colors.HexColor('#16A34A')

    # Styles typographiques personnalisés
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=COLOR_TERRACOTTA,
        alignment=TA_LEFT,
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_GRAY,
        alignment=TA_LEFT,
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_TERRACOTTA,
        spaceAfter=6,
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=COLOR_DARK,
    )

    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=COLOR_DARK,
    )

    cell_right = ParagraphStyle(
        'TableCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=COLOR_DARK,
        alignment=TA_RIGHT,
    )

    cell_right_bold = ParagraphStyle(
        'TableCellRightBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=COLOR_DARK,
        alignment=TA_RIGHT,
    )

    story = []

    restaurant = order.restaurant
    resto_name = restaurant.name if restaurant else "Le Gout"
    resto_tagline = restaurant.tagline if restaurant else "Saveurs Authentiques du Terroir Camerounais"
    resto_addr = restaurant.address if restaurant else "Boulevard de la Liberté, Akwa"
    resto_city = restaurant.city if restaurant else "Yaoundé"
    resto_phone = restaurant.phone if restaurant else "+237 690 12 34 56"

    # En-tête : Restaurant & Logo à gauche, Facture N° & Date à droite
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
    has_logo = os.path.exists(logo_path)

    if has_logo:
        logo_img = RLImage(logo_path, width=46, height=46)
        header_data = [
            [
                logo_img,
                Paragraph(f"<b><font size=11 color='#A83B19'>{resto_name}</font></b><br/><font size=8 color='#6B7280'>{resto_tagline}<br/>{resto_addr}, {resto_city}<br/>Tél: {resto_phone}</font>", styles['Normal']),
                Paragraph(f"<font color='#A83B19'><b>REÇU DE COMMANDE</b></font><br/><font size=9><b>Réf :</b> {order.order_number}<br/><b>Date :</b> {order.created_at.strftime('%d/%m/%Y à %H:%M')}</font>", cell_right)
            ]
        ]
        header_table = Table(header_data, colWidths=[54, 256, 210])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
    else:
        header_data = [
            [
                Paragraph(f"<b><font size=11 color='#A83B19'>{resto_name}</font></b><br/><font size=8 color='#6B7280'>{resto_tagline}<br/>{resto_addr}, {resto_city}<br/>Tél: {resto_phone}</font>", styles['Normal']),
                Paragraph(f"<font color='#A83B19'><b>REÇU DE COMMANDE</b></font><br/><font size=9><b>Réf :</b> {order.order_number}<br/><b>Date :</b> {order.created_at.strftime('%d/%m/%Y à %H:%M')}</font>", cell_right)
            ]
        ]
        header_table = Table(header_data, colWidths=[310, 210])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
    story.append(header_table)

    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_TERRACOTTA, spaceBefore=4, spaceAfter=12))

    # Badge de Statut de Paiement / Remboursement
    is_refunded = (order.payment_status == 'refunded' or order.status == 'refusee' or (hasattr(order, 'invoice') and order.invoice.is_refunded))
    if is_refunded:
        status_text = "<font color='#DC2626'><b>STATUT : COMMANDE REFUSÉE & REMBOURSÉE (100%)</b></font>"
        bg_badge = colors.HexColor('#FEE2E2')
        border_badge = COLOR_RED
    elif order.payment_status == 'paid':
        status_text = "<font color='#16A34A'><b>STATUT : PAIEMENT VALIDÉ & CONFIRMÉ</b></font>"
        bg_badge = colors.HexColor('#DCFCE7')
        border_badge = COLOR_GREEN
    else:
        status_text = f"<font color='#C27A23'><b>STATUT : PAIEMENT EN ATTENTE ({order.get_payment_method_display()})</b></font>"
        bg_badge = colors.HexColor('#FEF3C7')
        border_badge = COLOR_OCHRE

    badge_table = Table([[Paragraph(f"<para align=center>{status_text}</para>", styles['Normal'])]], colWidths=[520])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_badge),
        ('BOX', (0, 0), (-1, -1), 1, border_badge),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 14))

    # Bloc Coordonnées Client & Réception
    client_name = order.client.get_full_name() or order.client.username
    client_phone = order.delivery_phone or order.client.phone or "Non renseigné"
    mode_str = "Livraison à domicile" if order.delivery_type == 'delivery' else "À emporter / Retrait au restaurant"
    address_str = f"{order.delivery_address}, {order.delivery_neighborhood}" if order.delivery_type == 'delivery' else f"Comptoir de retrait ({resto_addr})"
    if order.delivery_type == 'delivery' and order.delivery_landmark:
        address_str += f" - Repère: {order.delivery_landmark}"

    info_data = [
        [
            Paragraph(f"<b>Informations Client :</b><br/>"
                      f"Nom : {client_name}<br/>"
                      f"Téléphone : {client_phone}<br/>"
                      f"Email : {order.client.email or 'N/A'}", cell_style),
            Paragraph(f"<b>Détails de Réception :</b><br/>"
                      f"Mode : <b>{mode_str}</b><br/>"
                      f"Lieu : {address_str}<br/>"
                      f"Règlement : {order.get_payment_method_display()}", cell_style),
        ]
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5DCD0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Tableau des Plats commandés
    story.append(Paragraph("<b>Détail des mets et boissons commandés :</b>", section_heading))

    items_data = [
        [
            Paragraph("<b>N°</b>", cell_bold),
            Paragraph("<b>Plat / Boisson</b>", cell_bold),
            Paragraph("<b>Options / Instructions</b>", cell_bold),
            Paragraph("<b>Qté</b>", cell_right_bold),
            Paragraph("<b>Prix Unit.</b>", cell_right_bold),
            Paragraph("<b>Sous-total</b>", cell_right_bold),
        ]
    ]

    for idx, item in enumerate(order.items.all(), 1):
        details = []
        if item.selected_side:
            details.append(f"Accompagnement: {item.selected_side}")
        if item.special_instructions:
            details.append(f"Note: {item.special_instructions}")
        details_str = "<br/>".join(details) if details else "-"

        items_data.append([
            Paragraph(str(idx), cell_style),
            Paragraph(f"<b>{item.dish_name}</b>", cell_style),
            Paragraph(f"<font size=8 color='#6B7280'>{details_str}</font>", cell_style),
            Paragraph(str(item.quantity), cell_right),
            Paragraph(f"{item.unit_price:,} F".replace(',', ' '), cell_right),
            Paragraph(f"<b>{item.subtotal:,} F</b>".replace(',', ' '), cell_right_bold),
        ])

    items_table = Table(items_data, colWidths=[25, 170, 145, 35, 65, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3EDE2')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_TERRACOTTA),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5DCD0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Récapitulatif Financier (Sous-total, Frais livraison, Total)
    fee_str = f"{order.delivery_fee:,} F CFA".replace(',', ' ') if order.delivery_fee > 0 else "0 F CFA (Offert / À emporter)"
    totals_data = [
        [Paragraph("Sous-total plats et boissons :", cell_style), Paragraph(f"<b>{order.subtotal:,} F CFA</b>".replace(',', ' '), cell_right)],
        [Paragraph("Frais de livraison :", cell_style), Paragraph(fee_str, cell_right)],
        [Paragraph("<font size=11 color='#A83B19'><b>TOTAL NET PAYÉ :</b></font>", cell_style),
         Paragraph(f"<font size=12 color='#A83B19'><b>{order.total_amount:,} F CFA</b></font>".replace(',', ' '), cell_right)],
    ]
    if is_refunded:
        totals_data.append([
            Paragraph("<font size=10 color='#DC2626'><b>MONTANT TOTAL REMBOURSÉ :</b></font>", cell_style),
            Paragraph(f"<font size=11 color='#DC2626'><b>{order.total_amount:,} F CFA</b></font>".replace(',', ' '), cell_right),
        ])

    totals_table = Table(totals_data, colWidths=[340, 180])
    totals_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 2), (-1, 2), 1, COLOR_TERRACOTTA),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 25))

    # Pied de page légal et culturel
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D1D5DB'), spaceBefore=5, spaceAfter=8))
    footer_text = (
        f"<font size=8 color='#6B7280'>"
        f"Document généré automatiquement par le système Le Gout le {order.updated_at.strftime('%d/%m/%Y à %H:%M')}. "
        f"Merci d'honorer la cuisine camerounaise authentique. En cas de réclamation, contactez le restaurant au {resto_phone}."
        f"</font>"
    )
    story.append(Paragraph(footer_text, styles['Normal']))

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value
