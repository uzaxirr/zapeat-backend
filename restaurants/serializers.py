from rest_framework import serializers
from restaurants.models import Restaurant, Location, OpeningTime, BankAccount, MenuCategory, MenuItem, \
    CustomizationGroup, CustomizationOption


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'longitude', 'latitude', 'location']

class OpeningTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningTime
        fields = ['id', 'weekday', 'from_hour', 'to_hour']

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'account_name', 'account_number', 'ifsc_code', 'bank_name', 'branch_name']

class RestaurantSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=False, allow_null=True)
    opening_times = OpeningTimeSerializer(many=True, required=False)
    bank_accounts = BankAccountSerializer(many=True, required=False)

    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        location_data = validated_data.pop('location', None)
        opening_times_data = validated_data.pop('opening_times', [])
        bank_accounts_data = validated_data.pop('bank_accounts', [])

        # Create location if exists
        if location_data:
            location = Location.objects.create(**location_data)
            validated_data['location'] = location

        # Create restaurant
        restaurant = Restaurant.objects.create(**validated_data)

        # Handle opening times - use get_or_create to avoid duplicates
        for ot_data in opening_times_data:
            # Try to find existing opening time or create a new one
            opening_time, _ = OpeningTime.objects.get_or_create(
                weekday=ot_data['weekday'],
                from_hour=ot_data['from_hour'],
                to_hour=ot_data['to_hour']
            )
            restaurant.opening_times.add(opening_time)

        # Add bank accounts to the restaurant
        for ba_data in bank_accounts_data:
            bank_account = BankAccount.objects.create(**ba_data)
            restaurant.bank_accounts.add(bank_account)

        return restaurant

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        opening_times_data = validated_data.pop('opening_times', [])
        bank_accounts_data = validated_data.pop('bank_accounts', [])

        # Update location
        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                location = Location.objects.create(**location_data)
                instance.location = location
                instance.save()

        # Update restaurant fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update opening times
        if opening_times_data:
            instance.opening_times.clear()
            opening_times = [OpeningTime.objects.create(**ot_data) for ot_data in opening_times_data]
            instance.opening_times.set(opening_times)

        # Update bank accounts
        if bank_accounts_data:
            instance.bank_accounts.clear()
            bank_accounts = [BankAccount.objects.create(**ba_data) for ba_data in bank_accounts_data]
            instance.bank_accounts.set(bank_accounts)

        return instance

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class CustomizationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizationGroup
        fields = '__all__'


class CustomizationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizationOption
        fields = '__all__'
