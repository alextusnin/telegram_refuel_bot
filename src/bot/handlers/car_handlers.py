"""Car management handlers."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

# Initialize database service
db_service = DatabaseService()

async def add_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /addcar command to add a new car."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to create your account first."
            )
            return
        
        # Check if user already has cars
        existing_cars = db_service.get_user_cars(db_user.id)
        
        if not context.args:
            # Show help message
            help_message = (
                "🚗 Add New Car\n\n"
                "Usage: /addcar <car_name> [make] [model] [year] [license_plate]\n\n"
                "Examples:\n"
                "• /addcar My Honda Civic\n"
                "• /addcar \"Work Truck\" Ford F-150 2018 ABC123\n"
                "• /addcar Work Truck Ford F-150 2018 XYZ789\n\n"
                f"You currently have {len(existing_cars)} car(s)."
            )
            
            if existing_cars:
                help_message += "\n\nYour current cars:\n"
                for car in existing_cars:
                    status = "⭐" if car.is_default else "🚗"
                    help_message += f"{status} {car.name}"
                    if car.make and car.model:
                        help_message += f" ({car.make} {car.model})"
                    if car.year:
                        help_message += f" - {car.year}"
                    help_message += "\n"
            
            await update.message.reply_text(help_message)
            return
        
        # Parse arguments
        car_name = context.args[0]
        make = context.args[1] if len(context.args) > 1 else None
        model = context.args[2] if len(context.args) > 2 else None
        year = None
        license_plate = None
        
        # Try to parse year (should be a number)
        if len(context.args) > 3:
            try:
                year = int(context.args[3])
            except ValueError:
                license_plate = context.args[3]
        
        # License plate is the last argument if year was parsed, or the 4th argument
        if len(context.args) > 4:
            license_plate = context.args[4]
        elif len(context.args) == 4 and year is None:
            license_plate = context.args[3]
        
        # Check if car name already exists for this user
        for car in existing_cars:
            if car.name.lower() == car_name.lower():
                await update.message.reply_text(
                    f"❌ You already have a car named '{car_name}'. Please choose a different name."
                )
                return
        
        # Determine if this should be the default car
        is_default = len(existing_cars) == 0  # First car is automatically default
        
        # Create the car
        new_car = db_service.create_car(
            user_id=db_user.id,
            name=car_name,
            make=make,
            model=model,
            year=year,
            license_plate=license_plate,
            is_default=is_default
        )
        
        # Create success message
        success_message = (
            f"✅ Car Added Successfully!\n\n"
            f"🚗 Name: {new_car.name}\n"
        )
        
        if new_car.make and new_car.model:
            success_message += f"🏭 Make/Model: {new_car.make} {new_car.model}\n"
        if new_car.year:
            success_message += f"📅 Year: {new_car.year}\n"
        if new_car.license_plate:
            success_message += f"🔢 License Plate: {new_car.license_plate}\n"
        
        if new_car.is_default:
            success_message += f"\n⭐ This is now your default car!"
        
        success_message += f"\n\nUse /cars to see all your cars."
        
        await update.message.reply_text(success_message)
        logger.info(f"Added car '{new_car.name}' for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error in add_car_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't add your car right now. Please try again later."
        )

async def cars_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /cars command to show user's cars."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to create your account first."
            )
            return
        
        # Get user's cars
        cars = db_service.get_user_cars(db_user.id)
        
        if not cars:
            await update.message.reply_text(
                "🚗 You don't have any cars yet.\n\n"
                "Use /addcar to add your first car!"
            )
            return
        
        # Create cars list message
        cars_message = f"🚗 Your Cars ({len(cars)} total)\n\n"
        
        for i, car in enumerate(cars, 1):
            status = "⭐" if car.is_default else "🚗"
            cars_message += f"{status} {car.name}\n"
            
            if car.make and car.model:
                cars_message += f"   🏭 {car.make} {car.model}\n"
            if car.year:
                cars_message += f"   📅 {car.year}\n"
            if car.license_plate:
                cars_message += f"   🔢 {car.license_plate}\n"
            
            cars_message += f"   📅 Added: {car.created_at.strftime('%Y-%m-%d')}\n\n"
        
        cars_message += "Use /addcar to add more cars!"
        
        await update.message.reply_text(cars_message)
        logger.info(f"Showed cars for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error in cars_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't retrieve your cars right now. Please try again later."
        )

async def set_default_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /setdefault command to set a default car."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to create your account first."
            )
            return
        
        if not context.args:
            # Show help message
            cars = db_service.get_user_cars(db_user.id)
            
            if not cars:
                await update.message.reply_text(
                    "❌ You don't have any cars yet.\n\n"
                    "Use /addcar to add your first car!"
                )
                return
            
            help_message = (
                "⭐ Set Default Car\n\n"
                "Usage: /setdefault <car_name>\n\n"
                "Your cars:\n"
            )
            
            for car in cars:
                status = "⭐" if car.is_default else "🚗"
                help_message += f"{status} {car.name}\n"
            
            help_message += "\nExample: /setdefault My Honda Civic"
            
            await update.message.reply_text(help_message)
            return
        
        # Get car name from arguments
        car_name = " ".join(context.args)
        
        # Find the car by name
        cars = db_service.get_user_cars(db_user.id)
        target_car = None
        
        for car in cars:
            if car.name.lower() == car_name.lower():
                target_car = car
                break
        
        if not target_car:
            await update.message.reply_text(
                f"❌ Car '{car_name}' not found.\n\n"
                "Use /cars to see your available cars."
            )
            return
        
        # Set as default
        success = db_service.set_default_car(target_car.id, db_user.id)
        
        if success:
            await update.message.reply_text(
                f"✅ '{target_car.name}' is now your default car! ⭐"
            )
            logger.info(f"Set default car '{target_car.name}' for user {user.id}")
        else:
            await update.message.reply_text(
                "❌ Failed to set default car. Please try again."
            )
        
    except Exception as e:
        logger.error(f"Error in set_default_car_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't set your default car right now. Please try again later."
        )

async def delete_car_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /deletecar command to delete a car."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to create your account first."
            )
            return
        
        if not context.args:
            # Show help message
            cars = db_service.get_user_cars(db_user.id)
            
            if not cars:
                await update.message.reply_text(
                    "❌ You don't have any cars yet.\n\n"
                    "Use /addcar to add your first car!"
                )
                return
            
            help_message = (
                "🗑️ Delete Car\n\n"
                "⚠️ WARNING: This will permanently delete the car and ALL its refuel entries!\n\n"
                "Usage: /deletecar <car_name>\n\n"
                "Your cars:\n"
            )
            
            for car in cars:
                status = "⭐" if car.is_default else "🚗"
                refuel_count = db_service.get_car_refuel_count(car.id, db_user.id)
                help_message += f"{status} {car.name}"
                if refuel_count > 0:
                    help_message += f" ({refuel_count} refuel entries)"
                help_message += "\n"
            
            help_message += "\nExample: /deletecar My Honda Civic"
            
            await update.message.reply_text(help_message)
            return
        
        # Get car name from arguments
        car_name = " ".join(context.args)


        
        # Find the car by name
        cars = db_service.get_user_cars(db_user.id)
        target_car = None
        
        for car in cars:
            if car.name.lower() == car_name.lower():
                target_car = car
                break
        
        if not target_car:
            await update.message.reply_text(
                f"❌ Car '{car_name}' not found.\n\n"
                "Use /cars to see your available cars."
            )
            return
        
        # Get refuel count for warning
        refuel_count = db_service.get_car_refuel_count(target_car.id, db_user.id)
        
        # Check if this is the only car
        if len(cars) == 1:
            await update.message.reply_text(
                "❌ Cannot delete your only car!\n\n"
                "You must have at least one car in your account.\n"
                "Add another car first with /addcar, then you can delete this one."
            )
            return
        
        # Show confirmation message
        confirmation_message = (
            f"⚠️ Confirm Car Deletion\n\n"
            f"🚗 Car: {target_car.name}\n"
        )
        
        if target_car.make and target_car.model:
            confirmation_message += f"🏭 Make/Model: {target_car.make} {target_car.model}\n"
        if target_car.year:
            confirmation_message += f"📅 Year: {target_car.year}\n"
        if target_car.license_plate:
            confirmation_message += f"🔢 License Plate: {target_car.license_plate}\n"
        
        if refuel_count > 0:
            confirmation_message += f"⛽ Refuel entries: {refuel_count}\n"
        
        if target_car.is_default:
            confirmation_message += f"⭐ This is your default car\n"
        
        confirmation_message += (
            f"\n⚠️ This action will:\n"
            f"• Permanently delete the car\n"
            f"• Delete ALL {refuel_count} refuel entries\n"
        )
        
        if target_car.is_default:
            confirmation_message += f"• Set another car as default\n"
        
        confirmation_message += (
            f"\nTo confirm, type: /deletecar_confirm {car_name}\n"
            f"To cancel, just ignore this message."
        )
        
        await update.message.reply_text(confirmation_message)
        
    except Exception as e:
        logger.error(f"Error in delete_car_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't process your request right now. Please try again later."
        )

async def delete_car_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the confirmation of car deletion."""
    user = update.effective_user
    
    try:
        # Get user from database
        db_user = db_service.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text(
                "❌ User not found. Please use /start to create your account first."
            )
            return
        
        # if not context.args or len(context.args) < 2 or context.args[0].lower() != 'confirm':
        #     await update.message.reply_text(
        #         "❌ Invalid confirmation format.\n\n"
        #         "Use: /deletecar confirm <car_name>\n\n"
        #         f"the context is '{context.args[0]}'"
        #     )
        #     return
        
        # Get car name from arguments (skip 'confirm')
        car_name = " ".join(context.args)

        
        # Find the car by name
        cars = db_service.get_user_cars(db_user.id)
        target_car = None
        
        for car in cars:
            if car.name.lower() == car_name.lower():
                target_car = car
                break
        
        if not target_car:
            await update.message.reply_text(
                f"❌ Car '{car_name}' not found.\n\n"
                "Use /cars to see your available cars."
                
            )
            return
        
        # Get refuel count before deletion
        refuel_count = db_service.get_car_refuel_count(target_car.id, db_user.id)
        car_name_to_delete = target_car.name
        was_default = target_car.is_default
        
        # Delete the car
        success = db_service.delete_car(target_car.id, db_user.id)
        
        if success:
            success_message = (
                f"✅ Car Deleted Successfully!\n\n"
                f"🚗 Deleted: {car_name_to_delete}\n"
                f"⛽ Removed {refuel_count} refuel entries\n"
            )
            
            if was_default:
                # Get the new default car
                new_default = db_service.get_default_car(db_user.id)
                if new_default:
                    success_message += f"⭐ New default car: {new_default.name}"
                else:
                    success_message += f"⭐ No default car set"
            
            await update.message.reply_text(success_message)
            logger.info(f"Deleted car '{car_name_to_delete}' for user {user.id}")
        else:
            await update.message.reply_text(
                "❌ Failed to delete car. Please try again."
            )
        
    except Exception as e:
        logger.error(f"Error in delete_car_confirm_handler: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't delete your car right now. Please try again later."
        )
