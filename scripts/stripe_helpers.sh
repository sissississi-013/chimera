#!/bin/bash
# Chimera Stripe Helper Commands
# Common Stripe CLI operations for marketplace development

echo "🧬 Chimera Stripe Helper Commands"
echo "=================================="
echo ""

# Function to display menu
show_menu() {
    echo "Available commands:"
    echo ""
    echo "1. Check Stripe Balance"
    echo "2. List Recent Products"
    echo "3. Create Test Product (Molecule Listing)"
    echo "4. List Recent Prices"
    echo "5. Create Test Price"
    echo "6. List Recent Customers"
    echo "7. Create Test Customer"
    echo "8. Create Test Payment Intent"
    echo "9. List Recent Payment Intents"
    echo "10. Listen to Webhooks (for testing)"
    echo "11. View Stripe Logs"
    echo "0. Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (0-11): " choice
    echo ""

    case $choice in
        0)
            echo "Goodbye!"
            exit 0
            ;;
        1)
            echo "📊 Checking Stripe Balance..."
            stripe balance retrieve
            ;;
        2)
            echo "📦 Listing Recent Products..."
            stripe products list --limit 10
            ;;
        3)
            echo "🧬 Creating Test Molecule Product..."
            read -p "Enter molecule name (e.g., EGFR_inhibitor_001): " mol_name
            read -p "Enter description: " mol_desc
            stripe products create \
                --name "$mol_name" \
                --description "$mol_desc" \
                --metadata[type]="molecule" \
                --metadata[smiles]="CC(=O)Oc1ccccc1C(=O)O" \
                --metadata[molecular_weight]="180.16"
            ;;
        4)
            echo "💰 Listing Recent Prices..."
            stripe prices list --limit 10
            ;;
        5)
            echo "💵 Creating Test Price..."
            read -p "Enter product ID (prod_...): " prod_id
            read -p "Enter price in cents (e.g., 50000 for $500.00): " price_cents
            stripe prices create \
                --product "$prod_id" \
                --unit-amount "$price_cents" \
                --currency usd
            ;;
        6)
            echo "👥 Listing Recent Customers..."
            stripe customers list --limit 10
            ;;
        7)
            echo "👤 Creating Test Customer..."
            read -p "Enter email: " cust_email
            read -p "Enter name: " cust_name
            stripe customers create \
                --email "$cust_email" \
                --name "$cust_name" \
                --description "Test customer for Chimera marketplace"
            ;;
        8)
            echo "💳 Creating Test Payment Intent..."
            read -p "Enter amount in cents (e.g., 50000 for $500.00): " amount
            stripe payment_intents create \
                --amount "$amount" \
                --currency usd \
                --payment-method-types card \
                --description "Molecule purchase from Chimera"
            ;;
        9)
            echo "📝 Listing Recent Payment Intents..."
            stripe payment_intents list --limit 10
            ;;
        10)
            echo "🎧 Starting Webhook Listener..."
            echo "This will forward Stripe events to http://localhost:8000/api/webhook/stripe"
            echo "Press Ctrl+C to stop"
            echo ""
            stripe listen --forward-to localhost:8000/api/webhook/stripe
            ;;
        11)
            echo "📋 Viewing Recent Stripe Logs..."
            stripe logs tail
            ;;
        *)
            echo "❌ Invalid choice. Please enter a number between 0-11."
            ;;
    esac

    echo ""
    echo "Press Enter to continue..."
    read
    clear
done
