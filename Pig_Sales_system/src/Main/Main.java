package Main;

import config.dbConnect;
import java.util.Scanner;
import java.util.List;
import java.util.Map;

public class Main {

    public static void viewPigs() {
        String Query = "SELECT pig_id, ear_tag, breed, weight, DATE_FORMAT(birth_date, '%Y-%m-%d') as birth_date, status, sale_price FROM tbl_pigs";
        
        String[] pigHeaders = {"Pig ID", "Ear Tag", "Breed", "Weight (kg)", "Birth Date", "Status", "Price"};
        String[] pigColumns = {"pig_id", "ear_tag", "breed", "weight", "birth_date", "status", "sale_price"};
        dbConnect conf = new dbConnect();
        conf.viewRecords(Query, pigHeaders, pigColumns);
    }

    public static void viewCustomers() {
        String Query = "SELECT * FROM tbl_customers";
        
        String[] customerHeaders = {"Customer ID", "First Name", "Last Name", "Contact", "Email", "Address"};
        String[] customerColumns = {"cust_id", "first_name", "last_name", "contact_num", "email_addr", "address"};
        dbConnect conf = new dbConnect();
        conf.viewRecords(Query, customerHeaders, customerColumns);
    }
    
    public static void viewSales() {
        String Query = "SELECT t_id, c.first_name, p.ear_tag, DATE_FORMAT(t.sale_date, '%Y-%m-%d') as sale_date, t.quantity, t.total_amount, t.payment_method "
                + "FROM tbl_sales_transactions t "
                + "JOIN tbl_customers c ON t.cust_id = c.cust_id "
                + "JOIN tbl_pigs p ON t.pig_id = p.pig_id";
        
        String[] saleHeaders = {"Trans ID", "Customer Name", "Pig/Batch Tag", "Date", "Quantity", "Total Amount", "Payment"};
        String[] saleColumns = {"t_id", "first_name", "ear_tag", "sale_date", "quantity", "total_amount", "payment_method"};
        dbConnect conf = new dbConnect();
        conf.viewRecords(Query, saleHeaders, saleColumns);
    }

    public static void viewUsers() {
        String Query = "SELECT * FROM tbl_user";
        
        String[] votersHeaders = {"ID", "Name", "Email", "Type", "Status"};
        String[] votersColumns = {"u_id", "u_name", "u_email", "u_type", "u_status"};
        dbConnect conf = new dbConnect();
        conf.viewRecords(Query, votersHeaders, votersColumns);
    }

    public static void addPig(Scanner sc, dbConnect con) {
        System.out.println("\n--- ADD NEW PIG TO INVENTORY ---");
        System.out.print("Enter Ear Tag/Batch Name: ");
        String earTag = sc.next();
        System.out.print("Enter Breed: ");
        String breed = sc.next();
        System.out.print("Enter Weight (kg): ");
        double weight = sc.nextDouble();
        System.out.print("Enter Birth Date (YYYY-MM-DD): ");
        String birthDate = sc.next();
        System.out.print("Enter Sale Price: ");
        double price = sc.nextDouble();
        
        String sql = "INSERT INTO tbl_pigs(ear_tag, breed, weight, birth_date, status, sale_price) VALUES (?, ?, ?, ?, ?, ?)";
        con.addRecord(sql, earTag, breed, weight, birthDate, "Available", price);
        System.out.println("✅ New Pig added to inventory successfully.");
    }
    
    public static void removePig(Scanner sc, dbConnect con) {
        System.out.println("\n--- REMOVE PIG FROM INVENTORY ---");
        viewPigs();
        System.out.print("Enter Pig ID to remove (DELETE): ");
        int pigId = sc.nextInt();
        
        String sql = "DELETE FROM tbl_pigs WHERE pig_id = ?";
        con.deleteRecord(sql, pigId);
        System.out.println("❌ Pig ID " + pigId + " removed successfully.");
    }

    public static void addSale(Scanner sc, dbConnect con) {
        System.out.println("\n--- RECORD NEW SALE ---");
        
        viewCustomers();
        System.out.print("Enter Customer ID for the sale (or 0 to add new customer): ");
        int custId = sc.nextInt();
        
        if (custId == 0) {
            System.out.println("\n--- ADD NEW CUSTOMER ---");
            System.out.print("Enter First Name: ");
            String fName = sc.next();
            System.out.print("Enter Last Name: ");
            String lName = sc.next();
            System.out.print("Enter Contact Number: ");
            String contact = sc.next();
            System.out.print("Enter Email Address: ");
            String email = sc.next();
            System.out.print("Enter Address: ");
            sc.nextLine();
            String address = sc.nextLine();
            
            String insertCustSql = "INSERT INTO tbl_customers(first_name, last_name, contact_num, email_addr, address) VALUES (?, ?, ?, ?, ?)";
            con.addRecord(insertCustSql, fName, lName, contact, email, address);
            
            String fetchCustIdSql = "SELECT cust_id FROM tbl_customers WHERE email_addr = ? ORDER BY cust_id DESC LIMIT 1";
            List<Map<String, Object>> result = con.fetchRecords(fetchCustIdSql, email);
            if (!result.isEmpty()) {
                custId = (int) result.get(0).get("cust_id");
            } else {
                System.out.println("Error: Could not retrieve new customer ID. Sale aborted.");
                return;
            }
        }
        
        String availableQuery = "SELECT pig_id, ear_tag, breed, weight, sale_price FROM tbl_pigs WHERE status = 'Available'";
        String[] availableHeaders = {"Pig ID", "Ear Tag", "Breed", "Weight (kg)", "Price"};
        String[] availableColumns = {"pig_id", "ear_tag", "breed", "weight", "sale_price"};
        con.viewRecords(availableQuery, availableHeaders, availableColumns);
        
        System.out.print("Enter Pig ID/Batch ID sold: ");
        int pigId = sc.nextInt();
        System.out.print("Enter Quantity: ");
        int quantity = sc.nextInt();
        System.out.print("Enter Total Sale Amount: ");
        double totalAmount = sc.nextDouble();
        System.out.print("Enter Payment Method: ");
        String paymentMethod = sc.next();

        String saleSql = "INSERT INTO tbl_sales_transactions(cust_id, pig_id, sale_date, quantity, total_amount, payment_method) VALUES (?, ?, CURDATE(), ?, ?, ?)";
        con.addRecord(saleSql, custId, pigId, quantity, totalAmount, paymentMethod);
        
        String updatePigSql = "UPDATE tbl_pigs SET status = 'Sold' WHERE pig_id = ?";
        con.updateRecord(updatePigSql, pigId);
        
        System.out.println("✅ Sale transaction recorded successfully. Pig/Batch status updated.");
    }
    
    public static void deleteSale(Scanner sc, dbConnect con) {
        System.out.println("\n--- DELETE SALES TRANSACTION ---");
        viewSales();
        System.out.print("Enter Transaction ID to delete: ");
        int transId = sc.nextInt();
        
        String sql = "DELETE FROM tbl_sales_transactions WHERE t_id = ?";
        con.deleteRecord(sql, transId);
        System.out.println("❌ Sales Transaction ID " + transId + " deleted successfully. (Note: Pig status is NOT automatically reverted).");
    }

    public static void main(String[] args) {
        dbConnect con = new dbConnect();
        con.connectDB();
        int choice;
        char cont;
        Scanner sc = new Scanner(System.in);

        do {
            System.out.println("\n===== PIG SALES MANAGEMENT SYSTEM =====");
            System.out.println("1. Login");
            System.out.println("2. Register");
            System.out.println("3. Exit");
            System.out.print("Enter choice: ");
            
            if (sc.hasNextInt()) {
                choice = sc.nextInt();
            } else {
                System.out.println("Invalid input. Please enter a number.");
                sc.next();
                choice = 0;
            }

            switch (choice) {
                case 1:
                    System.out.print("Enter email: ");
                    String em = sc.next();
                    System.out.print("Enter Password: ");
                    String pas = sc.next();
                    
                    while (true) {
                        String qry = "SELECT * FROM tbl_user WHERE u_email = ? AND u_pass = ?";
                        List<Map<String, Object>> result = con.fetchRecords(qry, em, pas);
                        
                        if (result.isEmpty()) {
                            System.out.println("INVALID CREDENTIALS");
                            break;
                        } else {
                            Map<String, Object> user = result.get(0);
                            String stat = user.get("u_status").toString();
                            String type = user.get("u_type").toString();
                            
                            if(stat.equals("Pending")){
                                System.out.println("Account is Pending, Contact the Admin!");
                                break;
                            } else {
                                System.out.println("LOGIN SUCCESS!");
                                
                                if(type.equals("Admin")){
                                    int adminChoice;
                                    do {
                                        System.out.println("\n--- ADMIN DASHBOARD ---");
                                        System.out.println("1. View Pig Inventory");
                                        System.out.println("2. View Customer Records");
                                        System.out.println("3. View Sales Transactions");
                                        System.out.println("4. Approve User Accounts (Management)");
                                        System.out.println("5. Logout");
                                        System.out.print("Enter choice: ");
                                        
                                        if (sc.hasNextInt()) {
                                            adminChoice = sc.nextInt();
                                        } else {
                                            System.out.println("Invalid input. Please enter a number.");
                                            sc.next();
                                            adminChoice = 0;
                                        }
                                        
                                        switch(adminChoice) {
                                            case 1: viewPigs(); break;
                                            case 2: viewCustomers(); break;
                                            case 3: viewSales(); break;
                                            case 4:
                                                viewUsers();
                                                System.out.print("Enter ID to Approve: ");
                                                int ids = sc.nextInt();
                                                String sql = "UPDATE tbl_user SET u_status = ? WHERE u_id = ?";
                                                con.updateRecord(sql, "Approved", ids);
                                                System.out.println("User ID " + ids + " approved.");
                                                break;
                                            case 5:
                                                System.out.println("Logging out...");
                                                break;
                                            default:
                                                System.out.println("Invalid choice.");
                                        }
                                    } while (adminChoice != 5);
                                    
                                } else if(type.equals("Staff")){ 
                                    int staffChoice;
                                    do {
                                        System.out.println("\n--- STAFF/SALES DASHBOARD ---");
                                        System.out.println("1. View Pig Inventory");
                                        System.out.println("2. Add New Pig");
                                        System.out.println("3. Remove Pig");
                                        System.out.println("4. Record New Sale Transaction");
                                        System.out.println("5. Delete Sale Transaction");
                                        System.out.println("6. View Customer Records");
                                        System.out.println("7. Logout");
                                        System.out.print("Enter choice: ");
                                        
                                        if (sc.hasNextInt()) {
                                            staffChoice = sc.nextInt();
                                        } else {
                                            System.out.println("Invalid input. Please enter a number.");
                                            sc.next();
                                            staffChoice = 0;
                                        }
                                        
                                        switch(staffChoice) {
                                            case 1: viewPigs(); break;
                                            case 2: addPig(sc, con); break;
                                            case 3: removePig(sc, con); break;
                                            case 4: addSale(sc, con); break;
                                            case 5: deleteSale(sc, con); break;
                                            case 6: viewCustomers(); break;
                                            case 7:
                                                System.out.println("Logging out...");
                                                break;
                                            default:
                                                System.out.println("Invalid choice.");
                                        }
                                    } while (staffChoice != 7);
                                }
                                break;
                            }
                        }
                    }
                    break;

                case 2:
                    System.out.print("Enter user name: ");
                    String name = sc.next();
                    System.out.print("Enter user email: ");
                    String email = sc.next();
                    
                    while (true) {
                        String qry = "SELECT * FROM tbl_user WHERE u_email = ?";
                        List<Map<String, Object>> result = con.fetchRecords(qry, email);

                        if (result.isEmpty()) {
                            break;
                        } else {
                            System.out.print("Email already exists, Enter other Email: ");
                            email = sc.next();
                        }
                    }

                    System.out.print("Enter user Type (1 - Admin/2 -Staff): ");
                    int type = sc.nextInt();
                    while(type > 2 || type < 1){
                        System.out.print("Invalid, choose between 1 & 2 only: ");
                        type = sc.nextInt();
                    }
                    String tp = (type == 1) ? "Admin" : "Staff";
                    
                    System.out.print("Enter Password: ");
                    String pass = sc.next();
                    
                    String sql = "INSERT INTO tbl_user(u_name, u_email, u_type, u_status, u_pass) VALUES (?, ?, ?, ?, ?)";
                    con.addRecord(sql, name, email, tp, "Pending", pass);
                    System.out.println("Registration successful. Your account is pending admin approval.");
                    break;

                case 3:
                    System.out.println("Exiting program...");
                    System.exit(0);
                    break;

                default:
                    System.out.println("Invalid choice.");
            }

            System.out.print("\nDo you want to continue in Main Menu? (Y/N): ");
            cont = sc.next().charAt(0);

        } while (cont == 'Y' || cont == 'y');

        System.out.println("Thank you! Program ended.");
    }
}